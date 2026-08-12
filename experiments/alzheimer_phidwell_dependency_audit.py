#!/usr/bin/env python3
"""Results-level audit of the 88-subject Phi-Dwell Alzheimer analysis.

No new classifier is fitted. We ask whether the headline metrics represent distinct
axes or mostly re-express the same token switching / word-frequency statistics.

Input is the committed JSON from BrainMetastabilityAnalyzerTool.
"""
from __future__ import annotations
import argparse, json, urllib.request
from pathlib import Path
import numpy as np
from scipy import stats

DEFAULT_URL = "https://raw.githubusercontent.com/anttiluode/BrainMetastabilityAnalyzerTool/main/Results/phidwell_alzheimer_results.json"
HEADLINE = ["vocab_size","entropy","mean_cv","top5_concentration","zipf_alpha"]
BANDS = ["delta","theta","alpha","beta","gamma"]


def rank_residual(y, X):
    y=np.asarray(y,float); X=np.asarray(X,float)
    ry=stats.rankdata(y)
    RX=np.column_stack([np.ones(len(y))]+[stats.rankdata(X[:,i]) for i in range(X.shape[1])])
    beta=np.linalg.lstsq(RX,ry,rcond=None)[0]
    return ry-RX@beta


def mw(a,b):
    u,p=stats.mannwhitneyu(a,b,alternative="two-sided")
    n1,n2=len(a),len(b)
    rb=1-2*u/(n1*n2)
    return {"n1":n1,"n2":n2,"mean1":float(np.mean(a)),"mean2":float(np.mean(b)),"U":float(u),"p":float(p),"rank_biserial":float(rb)}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--url",default=DEFAULT_URL); ap.add_argument("--out",default="results/alzheimer-phidwell-dependency-audit.json"); args=ap.parse_args()
    with urllib.request.urlopen(args.url,timeout=60) as r: raw=json.load(r)
    ids=sorted(raw)
    # Normalize group labels from either A/F/C or AD/FTD/CN variants.
    def norm(g):
        s=str(g).upper()
        if s in ("A","AD"): return "AD"
        if s in ("F","FTD"): return "FTD"
        if s in ("C","CN","CONTROL"): return "CN"
        return s
    rows=[]
    for sid in ids:
        r=raw[sid]; m=r.get("metrics",r)
        row={"id":sid,"group":norm(r.get("group",m.get("group",""))),"mmse":r.get("mmse",m.get("mmse")),"duration_s":m.get("duration_s"),"n_words":m.get("n_words")}
        for k in HEADLINE+["self_rate","perplexity","criticality_fraction","mean_coupling","delta_theta_coupling","alpha_beta_coupling"]:
            row[k]=m.get(k)
        for b in BANDS:
            row[f"self_{b}"]=m.get("band_self_rates",{}).get(b)
            row[f"cv_{b}"]=m.get("band_cv",{}).get(b)
            row[f"dwell_{b}"]=m.get("band_mean_dwell",{}).get(b)
        rows.append(row)
    rows=[r for r in rows if r["group"] in ("AD","FTD","CN")]
    print("subjects",len(rows),{g:sum(r['group']==g for r in rows) for g in ('AD','FTD','CN')})
    print("durations",sorted(set(r['duration_s'] for r in rows)),"n_words",sorted(set(r['n_words'] for r in rows)))

    def vec(k): return np.array([float(r[k]) for r in rows],float)
    # Spearman dependence among headline summaries.
    corr={}
    for a in HEADLINE:
        corr[a]={}
        for b in HEADLINE:
            rho,p=stats.spearmanr(vec(a),vec(b)); corr[a][b]={"rho":float(rho),"p":float(p)}
    print("\nheadline Spearman rho")
    print("metric               "+" ".join(f"{b[:8]:>9s}" for b in HEADLINE))
    for a in HEADLINE:
        print(f"{a:20s} "+" ".join(f"{corr[a][b]['rho']:+9.3f}" for b in HEADLINE))

    # PCA on rank-normalized headline metrics: effective dimension of the 5 claimed markers.
    Z=np.column_stack([stats.zscore(stats.rankdata(vec(k))) for k in HEADLINE])
    _,s,Vt=np.linalg.svd(Z,full_matrices=False)
    eig=s*s/(len(rows)-1); frac=eig/eig.sum()
    pca={"variance_fraction":frac.tolist(),"cumulative":np.cumsum(frac).tolist(),"loadings":{HEADLINE[i]:Vt[:,i].tolist() for i in range(len(HEADLINE))}}
    print("\nheadline rank-PCA variance fractions",np.round(frac,4))

    # AD vs CN headline results as stored.
    group_results={}
    for k in HEADLINE:
        ad=[r[k] for r in rows if r['group']=='AD']; cn=[r[k] for r in rows if r['group']=='CN']
        group_results[k]=mw(ad,cn)
        print(f"raw {k:20s} p={group_results[k]['p']:.5g} rb={group_results[k]['rank_biserial']:+.3f}")

    # The simple dynamics used to create the words: five per-band self-transition rates.
    X=np.column_stack([vec(f"self_{b}") for b in BANDS])
    residual_results={}
    for k in HEADLINE:
        resid=rank_residual(vec(k),X)
        ad=resid[[r['group']=='AD' for r in rows]]; cn=resid[[r['group']=='CN' for r in rows]]
        residual_results[k]=mw(ad,cn)
        rho=np.corrcoef(stats.rankdata(vec(k)), stats.rankdata(vec('self_rate')))[0,1]
        residual_results[k]["rho_with_global_self_rate"]=float(rho)
        print(f"switch-controlled {k:12s} p={residual_results[k]['p']:.5g} rb={residual_results[k]['rank_biserial']:+.3f}")

    # Dwell variables alone as predictors of headline ranks: report rank-R2, descriptive only.
    Xd=np.column_stack([vec(f"dwell_{b}") for b in BANDS])
    switch_r2={}; dwell_r2={}
    for k in HEADLINE:
        y=stats.rankdata(vec(k))
        for name,XX,store in [("switch",X,switch_r2),("dwell",Xd,dwell_r2)]:
            A=np.column_stack([np.ones(len(y))]+[stats.rankdata(XX[:,i]) for i in range(XX.shape[1])])
            pred=A@np.linalg.lstsq(A,y,rcond=None)[0]
            ssr=np.sum((y-pred)**2); sst=np.sum((y-y.mean())**2)
            store[k]=float(1-ssr/sst)
    print("\nrank-R2 from 5 band self-transition rates",switch_r2)
    print("rank-R2 from 5 band mean dwells",dwell_r2)

    # MMSE residual associations after switching control.
    mmse_results={}
    valid=np.array([r['mmse'] is not None and np.isfinite(float(r['mmse'])) for r in rows])
    for k in HEADLINE:
        resid=rank_residual(vec(k),X)
        rho,p=stats.spearmanr(resid[valid],np.array([float(r['mmse']) for r in rows])[valid])
        mmse_results[k]={"rho":float(rho),"p":float(p),"n":int(valid.sum())}

    out={"source":args.url,"n":len(rows),"groups":{g:sum(r['group']==g for r in rows) for g in ('AD','FTD','CN')},"durations":sorted(set(r['duration_s'] for r in rows)),"n_words":sorted(set(r['n_words'] for r in rows)),"headline_spearman":corr,"headline_rank_pca":pca,"ad_vs_cn_raw":group_results,"ad_vs_cn_after_controlling_five_band_self_transition_rates":residual_results,"rank_r2_from_band_self_rates":switch_r2,"rank_r2_from_band_mean_dwells":dwell_r2,"mmse_after_switch_control":mmse_results,"guardrails":["The five headline summaries are not assumed independent; four are functions of the same word-frequency distribution and mean_cv is a dwell-run statistic.","Residualisation is descriptive and linear-in-ranks; it does not prove causality.","A raw-EEG phase-randomized surrogate test is still required to decide whether effects depend on cross-channel phase organization beyond per-channel spectra."]}
    p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2)); print("wrote",p)

if __name__=='__main__': main()
