#!/usr/bin/env python3
"""Hard null for the exploratory RepOD physical-geometry + mode-energy effect.

For each subject we compute label-invariant cross-band AMI from dominant graph modes
using actual 10-20 geometry and mean squared projected energy. Then independently
Fourier-phase randomize every EEG channel, preserving each channel's exact magnitude
spectrum/autocorrelation, and recompute the same metric.

The load-bearing quantity is subject-level EXCESS = observed AMI - mean surrogate AMI.
If HC-vs-SZ separation disappears in excess, the apparent geometric effect is explained
by marginal spectral structure rather than multichannel phase/timing organization.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from scipy.stats import ttest_ind, ttest_rel

from repod_geometric_metric_audit import (
    ensure_dataset, load_preprocess, geometry_modes, dominant_sequences,
    ami_coupling, phase_randomize_channels, PAPER_EXCLUDE,
)


def effect(hc, sz):
    hc=np.asarray(hc,float); sz=np.asarray(sz,float)
    t,p=ttest_ind(hc,sz,equal_var=True)
    pooled=np.sqrt(((len(hc)-1)*hc.var(ddof=1)+(len(sz)-1)*sz.var(ddof=1))/(len(hc)+len(sz)-2))
    d=(sz.mean()-hc.mean())/pooled if pooled>0 else float('nan')
    return {"hc_mean":float(hc.mean()),"sz_mean":float(sz.mean()),"p":float(p),"t_hc_minus_sz":float(t),"cohen_d_sz_minus_hc":float(d),"n_hc":len(hc),"n_sz":len(sz)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data',default='data/repod_schizophrenia')
    ap.add_argument('--out',default='results/repod-geometry-energy-surrogate.json')
    ap.add_argument('--surrogates',type=int,default=4)
    ap.add_argument('--no-ica',action='store_true')
    args=ap.parse_args()
    rng=np.random.default_rng(20260812)
    paths=ensure_dataset(Path(args.data))
    rows=[]
    for k,path in enumerate(paths,1):
        group='HC' if path.name.startswith('h') else 'SZ'
        print(f'[{k:02d}/{len(paths)}] {path.name} {group}',flush=True)
        data,names,sfreq,removed=load_preprocess(path,use_ica=not args.no_ica)
        n=min(19,data.shape[0]); data=data[:n]; names=names[:n]
        geom=geometry_modes(names)
        obs=ami_coupling(dominant_sequences(data,sfreq,geom,'energy'))
        dur=min(int(60*sfreq),data.shape[1]); base=data[:,:dur]
        sur=[]
        for s in range(args.surrogates):
            xr=phase_randomize_channels(base,rng)
            sur.append(ami_coupling(dominant_sequences(xr,sfreq,geom,'energy')))
        sm=float(np.mean(sur))
        row={"file":path.name,"group":group,"ica_removed":removed,"observed_ami":float(obs),"surrogate_ami":list(map(float,sur)),"surrogate_mean":sm,"excess_ami":float(obs-sm)}
        rows.append(row)
        print(f'  observed={obs:+.5f} surrogate={sm:+.5f} excess={obs-sm:+.5f}',flush=True)

    clean=[r for r in rows if r['file'] not in PAPER_EXCLUDE]
    def vals(key,g): return [r[key] for r in clean if r['group']==g]
    result={
        "observed":effect(vals('observed_ami','HC'),vals('observed_ami','SZ')),
        "surrogate_mean":effect(vals('surrogate_mean','HC'),vals('surrogate_mean','SZ')),
        "excess_vs_spectrum_preserving_null":effect(vals('excess_ami','HC'),vals('excess_ami','SZ')),
        "within_group_observed_vs_surrogate":{},
        "paper_exclusions":sorted(PAPER_EXCLUDE),"surrogates_per_subject":args.surrogates,"subjects":rows,
        "guardrail":"Independent Fourier phase randomization preserves each channel's magnitude spectrum and hence linear autocorrelation while destroying cross-channel phase/timing structure. A surviving HC/SZ difference in observed-minus-surrogate excess is required before interpreting the metric as geometric coordination rather than transformed spectral structure."
    }
    for g in ('HC','SZ'):
        o=np.asarray(vals('observed_ami',g)); s=np.asarray(vals('surrogate_mean',g)); t,p=ttest_rel(o,s)
        result['within_group_observed_vs_surrogate'][g]={"mean_excess":float(np.mean(o-s)),"paired_t":float(t),"p":float(p)}
    print('\nOBSERVED',json.dumps(result['observed'],indent=2))
    print('\nSURROGATE GROUP EFFECT',json.dumps(result['surrogate_mean'],indent=2))
    print('\nEXCESS GROUP EFFECT',json.dumps(result['excess_vs_spectrum_preserving_null'],indent=2))
    print('\nWITHIN GROUP',json.dumps(result['within_group_observed_vs_surrogate'],indent=2))
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2)); print('wrote',out)

if __name__=='__main__': main()
