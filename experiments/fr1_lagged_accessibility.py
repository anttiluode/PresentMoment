#!/usr/bin/env python3
"""Lag-resolved source->receiver accessibility in real human FR1 iEEG.

This is an independent second measure after the PTE calibration. It does NOT call
lagged prediction 'causal transmission'. The question is narrower:

    At what source lags does a source region improve cross-validated prediction of
    the target beyond the target's own recent history, and how much of that survives
    a trial-mismatch null that preserves each region's spectrum/autocorrelation and
    task-event timing?

Why trial mismatch?
-------------------
For condition-matched trials, source trial j is paired with target trial i. This
preserves source and target marginal temporal statistics and any stereotyped
stimulus-locked response, but destroys trial-specific source-target coordination.
Thus OBSERVED - MISMATCH is an 'excess accessibility' profile rather than a trivial
low-frequency memory effect.

We use the complex analytic band signal (real + Hilbert quadrature), not PTE. Target
real+imag at time t are ridge-predicted from a fixed set of target self-history lags;
the full model adds source real+imag at one candidate lag. Cross-validation holds out
whole trials to prevent overlapping time samples from leaking between train/test.

Guardrail: common trial-specific drive can still create excess predictive access.
This test identifies receiver-accessible source history, not the physical carrier.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, hilbert, resample_poly, sosfiltfilt

from fr1_pte_calibration import (
    BANDS, load_edf_channels, read_events, recall_epochs,
    successful_encoding_epochs, zscore,
)
from fr1_multi_subject_pte import select_pair

TARGET_FS = 100.0
SELF_LAGS_MS = (10, 20, 40, 80, 160, 320)
SOURCE_LAGS_MS = (10, 20, 40, 80, 120, 160, 240, 320, 480, 640)


def analytic_band(x: np.ndarray, sfreq: float, lo: float, hi: float) -> np.ndarray:
    sos = butter(4, [lo, hi], btype="bandpass", fs=sfreq, output="sos")
    y = sosfiltfilt(sos, x)
    return hilbert(y)


def epoch_analytic(z: np.ndarray, starts: np.ndarray, stops: np.ndarray, sfreq: float) -> list[np.ndarray]:
    # Downsample each already-full-record-filtered analytic epoch to 100 Hz.
    # Real and quadrature are resampled separately to avoid complex-library assumptions.
    down = int(round(sfreq / TARGET_FS))
    if abs(sfreq / down - TARGET_FS) > 1e-6:
        raise ValueError(f"Expected integer downsample to {TARGET_FS} Hz from {sfreq}")
    out=[]
    for a,b in zip(starts,stops):
        a,b=int(a),int(b)
        if a < 0 or b > len(z) or b <= a:
            continue
        seg=z[a:b]
        re=resample_poly(seg.real,1,down)
        im=resample_poly(seg.imag,1,down)
        n=min(len(re),len(im))
        if n >= 100:
            out.append(np.column_stack([re[:n],im[:n]]).astype(np.float64))
    if not out:
        raise RuntimeError("no valid epochs")
    n=min(len(q) for q in out)
    return [q[:n] for q in out]


def ms_to_samples(values):
    return tuple(max(1,int(round(v*TARGET_FS/1000.0))) for v in values)


def build_trial_rows(target_trials, source_trials, source_map, source_lag, self_lags):
    """Return per-trial (Xbase, Xfull, Y); source_map maps target trial -> source trial."""
    maxlag=max(max(self_lags),source_lag)
    rows=[]
    for i,targ in enumerate(target_trials):
        src=source_trials[int(source_map[i])]
        n=min(len(targ),len(src))
        if n <= maxlag+10:
            continue
        idx=np.arange(maxlag,n)
        # Target analytic self-history: real+quadrature at each fixed lag.
        xb=np.column_stack([targ[idx-l,:] for l in self_lags])
        xs=src[idx-source_lag,:]
        xf=np.column_stack([xb,xs])
        y=targ[idx,:]
        rows.append((xb,xf,y))
    return rows


def ridge_predict(Xtr,Ytr,Xte,alpha):
    xm=Xtr.mean(axis=0); xs=Xtr.std(axis=0); xs[xs<1e-10]=1.0
    ym=Ytr.mean(axis=0); ys=Ytr.std(axis=0); ys[ys<1e-10]=1.0
    A=(Xtr-xm)/xs; B=(Ytr-ym)/ys
    AtA=A.T@A
    beta=np.linalg.solve(AtA + alpha*np.eye(AtA.shape[0]), A.T@B)
    pred=((Xte-xm)/xs)@beta
    return pred,ym,ys


def cv_increment(rows, folds=5, alpha=10.0):
    """Cross-validated delta-R2(full minus target-history-only), grouped by trial."""
    ntr=len(rows)
    if ntr < folds+2:
        return float('nan')
    fold_id=np.arange(ntr)%folds
    sse_base=sse_full=sst=0.0
    for f in range(folds):
        train=[rows[i] for i in range(ntr) if fold_id[i]!=f]
        test=[rows[i] for i in range(ntr) if fold_id[i]==f]
        xbtr=np.vstack([r[0] for r in train]); xftr=np.vstack([r[1] for r in train]); ytr=np.vstack([r[2] for r in train])
        xbte=np.vstack([r[0] for r in test]); xfte=np.vstack([r[1] for r in test]); yte=np.vstack([r[2] for r in test])
        pb,ym,ys=ridge_predict(xbtr,ytr,xbte,alpha)
        pf,ym2,ys2=ridge_predict(xftr,ytr,xfte,alpha)
        # Both fits use same Y train set, so scaling should be identical up to roundoff.
        yz=(yte-ym)/ys
        sse_base += float(np.sum((yz-pb)**2))
        sse_full += float(np.sum((yz-pf)**2))
        sst += float(np.sum(yz**2))
    if sst <= 0:
        return float('nan')
    return float((1-sse_full/sst) - (1-sse_base/sst))


def one_direction(target_trials, source_trials, permutations, seed, alpha):
    n=min(len(target_trials),len(source_trials))
    target_trials=target_trials[:n]; source_trials=source_trials[:n]
    self_lags=ms_to_samples(SELF_LAGS_MS)
    source_lags=ms_to_samples(SOURCE_LAGS_MS)
    identity=np.arange(n)
    rng=np.random.default_rng(seed)
    out=[]
    for lag_ms,lag in zip(SOURCE_LAGS_MS,source_lags):
        obs=cv_increment(build_trial_rows(target_trials,source_trials,identity,lag,self_lags),alpha=alpha)
        null=[]
        for _ in range(permutations):
            p=rng.permutation(n)
            # Avoid accidental identity; a derangement is unnecessary at n~80 but
            # ensure no permutation is globally unchanged.
            if np.all(p==identity):
                p=np.roll(p,1)
            v=cv_increment(build_trial_rows(target_trials,source_trials,p,lag,self_lags),alpha=alpha)
            if np.isfinite(v): null.append(v)
        null=np.asarray(null,float)
        nmean=float(np.mean(null)); excess=float(obs-nmean)
        p_emp=float((1+np.count_nonzero(null>=obs))/(1+len(null)))
        out.append({
            "lag_ms":lag_ms,"observed_delta_r2":float(obs),"mismatch_mean_delta_r2":nmean,
            "mismatch_sd":float(np.std(null)),"excess_delta_r2":excess,
            "one_sided_empirical_p":p_emp,"mismatch_draws":int(len(null)),
        })
    return out


def profile_summary(profile):
    lag=np.asarray([r['lag_ms'] for r in profile],float)
    ex=np.asarray([r['excess_delta_r2'] for r in profile],float)
    pos=np.maximum(ex,0)
    # Integral is descriptive. Centroid is undefined if no positive excess.
    area=float(np.trapezoid(pos,lag))
    centroid=float(np.sum(lag*pos)/np.sum(pos)) if pos.sum()>0 else float('nan')
    far=lag>=240
    far_area=float(np.trapezoid(pos[far],lag[far])) if np.count_nonzero(far)>=2 else 0.0
    sig_lags=[int(r['lag_ms']) for r in profile if r['one_sided_empirical_p']<=0.05 and r['excess_delta_r2']>0]
    return {"positive_excess_area_r2_ms":area,"positive_excess_lag_centroid_ms":centroid,"far_240ms_plus_area_r2_ms":far_area,"nominal_positive_lags_ms":sig_lags}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--subject',required=True); p.add_argument('--session',required=True)
    p.add_argument('--edf',type=Path,required=True); p.add_argument('--events',type=Path,required=True)
    p.add_argument('--permutations',type=int,default=40); p.add_argument('--alpha',type=float,default=10.0)
    p.add_argument('--out',type=Path,required=True); args=p.parse_args()

    sel=select_pair(args.subject,args.session)
    hip_ch=str(sel['hippocampal']['channel']); par_ch=str(sel['parietal']['channel'])
    print('selection',json.dumps(sel,indent=2))
    sfreq,hip,par=load_edf_channels(args.edf,(hip_ch,par_ch)); hip=zscore(hip); par=zscore(par)
    events=read_events(args.events)
    epoch_sets=(successful_encoding_epochs(events,sfreq),recall_epochs(events,sfreq))
    result={"subject":args.subject,"session":args.session,"selection":sel,"target_fs":TARGET_FS,
            "self_history_lags_ms":list(SELF_LAGS_MS),"source_probe_lags_ms":list(SOURCE_LAGS_MS),"bands":{},
            "guardrails":[
                "Trial mismatch preserves each region's marginal spectrum/autocorrelation and condition/event alignment but destroys trial-specific pairing.",
                "Excess predictive accessibility is not proof of a physical source-to-target carrier; trial-specific common drive can survive this test.",
                "No lag is interpreted from raw observed delta-R2 alone; the mismatch-subtracted profile is load-bearing.",
            ]}

    for bi,(band,(lo,hi)) in enumerate(BANDS.items()):
        print(f'\nBAND {band} {lo}-{hi} Hz',flush=True)
        hz=analytic_band(hip,sfreq,lo,hi); pz=analytic_band(par,sfreq,lo,hi)
        result['bands'][band]={}
        for ei,ep in enumerate(epoch_sets):
            he=epoch_analytic(hz,ep.starts,ep.stops,sfreq); pe=epoch_analytic(pz,ep.starts,ep.stops,sfreq)
            n=min(len(he),len(pe)); he=he[:n]; pe=pe[:n]
            hp=one_direction(pe,he,args.permutations,10000+bi*1000+ei*100,args.alpha) # source H -> target P
            ph=one_direction(he,pe,args.permutations,20000+bi*1000+ei*100,args.alpha) # source P -> target H
            # Directional excess per lag, analogous in spirit to PTE-DI but independent estimator.
            directional=[]
            for a,b in zip(hp,ph):
                directional.append({"lag_ms":a['lag_ms'],"hipp_to_par_excess_minus_par_to_hipp_excess":float(a['excess_delta_r2']-b['excess_delta_r2'])})
            row={"n_trials":n,"hipp_to_parietal":{"profile":hp,"summary":profile_summary(hp)},
                 "parietal_to_hipp":{"profile":ph,"summary":profile_summary(ph)},"directional_excess_profile":directional}
            result['bands'][band][ep.name]=row
            print(f"{ep.name} n={n}")
            print('  H->P',json.dumps(row['hipp_to_parietal']['summary']))
            print('  P->H',json.dumps(row['parietal_to_hipp']['summary']))
            print('  dir excess',[(q['lag_ms'],round(q['hipp_to_par_excess_minus_par_to_hipp_excess'],6)) for q in directional])

    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(result,indent=2)); print('wrote',args.out)

if __name__=='__main__': main()
