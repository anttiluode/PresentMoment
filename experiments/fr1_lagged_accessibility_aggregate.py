#!/usr/bin/env python3
"""Aggregate the frozen six-subject FR1 lagged-accessibility gate.

Primary frozen contrast:
  for each participant, average mismatch-subtracted far-history area (>=240 ms)
  across encoding/recall and both directions, then compute

      delta_theta - beta.

A positive participant-level contrast means more trial-specific recoverable history
at long lags in delta/theta than beta after the condition-matched trial-mismatch null.

N=6 is a calibration gate, not population proof. We report the exact sign-flip
permutation p over the 2^6 participant sign assignments, plus raw subject values.
"""
from __future__ import annotations
import argparse, glob, json, math
from pathlib import Path
import numpy as np

BANDS=("delta_theta","beta")
EPOCHS=("successful_encoding","recall")
DIRS=("hipp_to_parietal","parietal_to_hipp")


def exact_signflip_p(x):
    x=np.asarray(x,float); obs=abs(float(np.mean(x)))
    vals=[]
    for mask in range(1<<len(x)):
        s=np.array([1.0 if (mask>>i)&1 else -1.0 for i in range(len(x))])
        vals.append(abs(float(np.mean(x*s))))
    vals=np.asarray(vals)
    return float(np.mean(vals >= obs-1e-15))


def mean_far(r, band):
    vals=[]
    for ep in EPOCHS:
        for d in DIRS:
            vals.append(float(r['bands'][band][ep][d]['summary']['far_240ms_plus_area_r2_ms']))
    return float(np.mean(vals))


def mean_centroid(r, band):
    vals=[]
    for ep in EPOCHS:
        for d in DIRS:
            v=float(r['bands'][band][ep][d]['summary']['positive_excess_lag_centroid_ms'])
            if np.isfinite(v): vals.append(v)
    return float(np.mean(vals)) if vals else float('nan')


def route_far(r, band, direction):
    return float(np.mean([r['bands'][band][ep][direction]['summary']['far_240ms_plus_area_r2_ms'] for ep in EPOCHS]))


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--out',required=True); args=ap.parse_args()
    files=sorted(glob.glob(str(Path(args.root)/'**/fr1-lagged-accessibility-*.json'),recursive=True))
    rows=[]
    for f in files:
        try: r=json.load(open(f))
        except Exception: continue
        if 'bands' not in r: continue
        dt=mean_far(r,'delta_theta'); be=mean_far(r,'beta')
        row={
            'subject':r['subject'],'session':str(r['session']),
            'delta_theta_far_area_mean':dt,'beta_far_area_mean':be,
            'primary_far_area_dt_minus_beta':dt-be,
            'delta_theta_centroid_mean_ms':mean_centroid(r,'delta_theta'),
            'beta_centroid_mean_ms':mean_centroid(r,'beta'),
            'centroid_dt_minus_beta_ms':mean_centroid(r,'delta_theta')-mean_centroid(r,'beta'),
            'dt_H_to_P_far':route_far(r,'delta_theta','hipp_to_parietal'),
            'dt_P_to_H_far':route_far(r,'delta_theta','parietal_to_hipp'),
            'beta_H_to_P_far':route_far(r,'beta','hipp_to_parietal'),
            'beta_P_to_H_far':route_far(r,'beta','parietal_to_hipp'),
        }
        row['published_route_like_contrast']=(row['dt_H_to_P_far']-row['dt_P_to_H_far']) + (row['beta_P_to_H_far']-row['beta_H_to_P_far'])
        rows.append(row)
    # Deduplicate by subject/session in case artifact layout repeats files.
    dedup={(r['subject'],r['session']):r for r in rows}; rows=[dedup[k] for k in sorted(dedup)]
    x=np.array([r['primary_far_area_dt_minus_beta'] for r in rows],float)
    c=np.array([r['centroid_dt_minus_beta_ms'] for r in rows],float)
    route=np.array([r['published_route_like_contrast'] for r in rows],float)
    out={
        'n':len(rows),'subjects':rows,
        'primary':{
            'name':'mean far-history excess area >=240ms: delta_theta minus beta',
            'mean':float(np.mean(x)) if len(x) else float('nan'),
            'median':float(np.median(x)) if len(x) else float('nan'),
            'positive_fraction':float(np.mean(x>0)) if len(x) else float('nan'),
            'exact_two_sided_signflip_p':exact_signflip_p(x) if len(x) else float('nan'),
        },
        'secondary_centroid':{
            'mean_dt_minus_beta_ms':float(np.nanmean(c)) if len(c) else float('nan'),
            'positive_fraction':float(np.mean(c>0)) if len(c) else float('nan'),
            'exact_two_sided_signflip_p':exact_signflip_p(c[np.isfinite(c)]) if np.any(np.isfinite(c)) else float('nan'),
        },
        'secondary_route_like':{
            'definition':'(DT H->P - DT P->H) + (beta P->H - beta H->P) far-history excess areas',
            'mean':float(np.mean(route)) if len(route) else float('nan'),
            'positive_fraction':float(np.mean(route>0)) if len(route) else float('nan'),
            'exact_two_sided_signflip_p':exact_signflip_p(route) if len(route) else float('nan'),
        },
        'guardrail':'Frozen six-subject outcome-blind anatomy cohort. N=6 is a directional calibration gate only. Raw band autocorrelation is not load-bearing; all summaries use observed-minus-trial-mismatch excess.'
    }
    print(json.dumps(out,indent=2)); p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2))

if __name__=='__main__': main()
