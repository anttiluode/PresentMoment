#!/usr/bin/env python3
"""Robustness audit for the exploratory RepOD physical-geometry effect.

Changes from the first repaired metric:
* canonical bands are filtered ONCE on a continuous 64 s segment, not separately
  inside every 0.5 s word;
* the outer 2 s on each side are discarded after filtering, leaving 60 s;
* graph neighbourhood k in {3,4,5,6} and retained mode count in {4,6,8} are varied;
* all coupling is label-invariant adjusted mutual information (AMI);
* spectrum-preserving independent-channel Fourier phase surrogates are rerun.

This is a stability audit, not 12 independent hypothesis tests. We care primarily
whether the SZ-HC sign and observed-minus-surrogate sign are stable across reasonable
analysis choices.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfiltfilt
from scipy.stats import ttest_ind
from sklearn.metrics import adjusted_mutual_info_score

from repod_geometric_metric_audit import ensure_dataset,load_preprocess,phase_randomize_channels,PAPER_EXCLUDE,BANDS

WORD_S=0.5
PAD_S=2.0
USE_S=60.0


def graph_modes(names,k,n_modes):
    import mne
    montage=mne.channels.make_standard_montage('standard_1020')
    lookup={a.upper():np.asarray(v,float) for a,v in montage.get_positions()['ch_pos'].items()}
    X=np.vstack([lookup[n.upper().replace(' ','')] for n in names])
    d=np.linalg.norm(X[:,None,:]-X[None,:,:],axis=2); n=len(names); A=np.zeros((n,n),float)
    for i in range(n):
        for j in np.argsort(d[i])[1:k+1]:
            w=1.0/max(float(d[i,j]),1e-9); A[i,j]=max(A[i,j],w); A[j,i]=max(A[j,i],w)
    L=np.diag(A.sum(axis=1))-A
    _,V=np.linalg.eigh(L)
    return V[:,:min(n_modes,n)]


def seq_fullfilter(data,sfreq,V):
    need=int((USE_S+2*PAD_S)*sfreq)
    x=data[:V.shape[0],:need]
    if x.shape[1] < need: raise RuntimeError('recording too short')
    a=int(PAD_S*sfreq); b=a+int(USE_S*sfreq); word=int(WORD_S*sfreq); nw=(b-a)//word
    out={}
    for name,(lo,hi) in BANDS.items():
        sos=butter(4,[lo,hi],btype='bandpass',fs=sfreq,output='sos')
        y=sosfiltfilt(sos,x,axis=1)[:,a:b]
        proj=y.T@V
        proj=proj[:nw*word].reshape(nw,word,V.shape[1])
        energy=np.mean(proj*proj,axis=1)
        out[name]=np.argmax(energy,axis=1).astype(int)
    return out


def ami(seq):
    vals=[]; names=list(BANDS)
    for i in range(len(names)):
        for j in range(i+1,len(names)):
            vals.append(adjusted_mutual_info_score(seq[names[i]],seq[names[j]]))
    return float(np.mean(vals))


def effect(rows,key):
    clean=[r for r in rows if r['file'] not in PAPER_EXCLUDE]
    hc=np.asarray([r[key] for r in clean if r['group']=='HC']); sz=np.asarray([r[key] for r in clean if r['group']=='SZ'])
    t,p=ttest_ind(hc,sz,equal_var=True)
    pooled=math.sqrt(((len(hc)-1)*hc.var(ddof=1)+(len(sz)-1)*sz.var(ddof=1))/(len(hc)+len(sz)-2))
    return {'hc_mean':float(hc.mean()),'sz_mean':float(sz.mean()),'p':float(p),'cohen_d_sz_minus_hc':float((sz.mean()-hc.mean())/pooled),'n_hc':len(hc),'n_sz':len(sz)}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data',default='data/repod_schizophrenia'); ap.add_argument('--out',default='results/repod-geometry-robustness.json'); ap.add_argument('--surrogates',type=int,default=3); args=ap.parse_args()
    variants=[(k,m) for k in (3,4,5,6) for m in (4,6,8)]
    paths=ensure_dataset(Path(args.data)); rng=np.random.default_rng(20260812)
    rows_by={f'k{k}_m{m}':[] for k,m in variants}
    for ii,path in enumerate(paths,1):
        group='HC' if path.name.startswith('h') else 'SZ'; print(f'[{ii:02d}/{len(paths)}] {path.name} {group}',flush=True)
        data,names,sfreq,removed=load_preprocess(path,use_ica=True); n=min(19,data.shape[0]); data=data[:n]; names=names[:n]
        need=int((USE_S+2*PAD_S)*sfreq); base=data[:,:need]
        surrogate_data=[phase_randomize_channels(base,rng) for _ in range(args.surrogates)]
        for k,m in variants:
            key=f'k{k}_m{m}'; V=graph_modes(names,k,m)
            obs=ami(seq_fullfilter(base,sfreq,V)); ss=[ami(seq_fullfilter(x,sfreq,V)) for x in surrogate_data]; sm=float(np.mean(ss))
            rows_by[key].append({'file':path.name,'group':group,'observed':obs,'surrogate_mean':sm,'excess':obs-sm})
    summaries={}
    for key,rows in rows_by.items():
        summaries[key]={'observed':effect(rows,'observed'),'surrogate':effect(rows,'surrogate_mean'),'excess':effect(rows,'excess')}
        s=summaries[key]
        print(f"{key:7s} OBS d={s['observed']['cohen_d_sz_minus_hc']:+.3f} p={s['observed']['p']:.4g} | SUR d={s['surrogate']['cohen_d_sz_minus_hc']:+.3f} p={s['surrogate']['p']:.4g} | EXCESS d={s['excess']['cohen_d_sz_minus_hc']:+.3f} p={s['excess']['p']:.4g}")
    obs_d=np.array([v['observed']['cohen_d_sz_minus_hc'] for v in summaries.values()]); ex_d=np.array([v['excess']['cohen_d_sz_minus_hc'] for v in summaries.values()]); ex_p=np.array([v['excess']['p'] for v in summaries.values()])
    stability={'variants':len(variants),'observed_positive_sign_fraction':float(np.mean(obs_d>0)),'excess_positive_sign_fraction':float(np.mean(ex_d>0)),'excess_nominal_p_lt_0_05_fraction':float(np.mean(ex_p<0.05)),'observed_d_range':[float(obs_d.min()),float(obs_d.max())],'excess_d_range':[float(ex_d.min()),float(ex_d.max())],'excess_median_p':float(np.median(ex_p))}
    result={'continuous_filtering':True,'analysis_segment_s':USE_S,'discarded_edge_s_each_side':PAD_S,'surrogates_per_subject':args.surrogates,'paper_exclusions':sorted(PAPER_EXCLUDE),'summaries_n26':summaries,'stability':stability,'guardrail':'This method family was specified only after the repaired k4/m6 effect was observed. Stability across choices reduces implementation fragility but is not an independent replication.'}
    print('\nSTABILITY',json.dumps(stability,indent=2)); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2)); print('wrote',out)

if __name__=='__main__': main()
