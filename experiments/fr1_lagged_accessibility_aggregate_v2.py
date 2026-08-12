#!/usr/bin/env python3
"""Re-audit the frozen six-subject FR1 history-depth contrast with a signed metric.

The first aggregate used profile_summary['far_240ms_plus_area_r2_ms'], which clips
negative excess to zero before integration. That is useful for describing where
positive excess exists inside one profile, but it is NOT suitable for comparing
bands: a noisier band gets a larger positive-only area even when its signed excess
is centered at zero.

This v2 aggregate therefore freezes a safer primitive:

    signed_far_area = integral_{240..640 ms} (observed delta-R2 - mismatch mean) dlag

computed directly from each stored lag profile, then averaged across encoding/recall
and both directions per participant. The band contrast is delta_theta - beta.

This correction was motivated by inspecting the statistic after the v1 frozen6 result,
so v2 is a sanity correction, not an independent preregistered test. Both v1 and v2
remain in the repository for auditability.
"""
from __future__ import annotations
import argparse, glob, json
from pathlib import Path
import numpy as np

EPOCHS=("successful_encoding","recall")
DIRS=("hipp_to_parietal","parietal_to_hipp")
FAR=(240,320,480,640)


def exact_signflip_p(x):
    x=np.asarray(x,float); obs=abs(float(np.mean(x))); vals=[]
    for mask in range(1<<len(x)):
        s=np.array([1.0 if (mask>>i)&1 else -1.0 for i in range(len(x))])
        vals.append(abs(float(np.mean(x*s))))
    return float(np.mean(np.asarray(vals)>=obs-1e-15))


def signed_far_area(profile):
    by={int(q['lag_ms']):q for q in profile}
    x=np.asarray(FAR,float)
    y=np.asarray([float(by[l]['excess_delta_r2']) for l in FAR],float)
    return float(np.trapezoid(y,x))


def participant_band(r,band):
    vals=[]
    for ep in EPOCHS:
        for d in DIRS:
            vals.append(signed_far_area(r['bands'][band][ep][d]['profile']))
    return float(np.mean(vals))


def participant_lag(r,band,lag):
    vals=[]
    for ep in EPOCHS:
        for d in DIRS:
            by={int(q['lag_ms']):q for q in r['bands'][band][ep][d]['profile']}
            vals.append(float(by[lag]['excess_delta_r2']))
    return float(np.mean(vals))


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--out',required=True); args=ap.parse_args()
    files=sorted(glob.glob(str(Path(args.root)/'**/fr1-lagged-accessibility-*.json'),recursive=True))
    rows=[]
    for f in files:
        try: r=json.load(open(f))
        except Exception: continue
        if 'bands' not in r: continue
        dt=participant_band(r,'delta_theta'); be=participant_band(r,'beta')
        row={'subject':r['subject'],'session':str(r['session']),'delta_theta_signed_far_area':dt,'beta_signed_far_area':be,'dt_minus_beta_signed_far_area':dt-be}
        row['lag_contrasts']={str(lag):participant_lag(r,'delta_theta',lag)-participant_lag(r,'beta',lag) for lag in (10,20,40,80,120,160,240,320,480,640)}
        rows.append(row)
    dedup={(r['subject'],r['session']):r for r in rows}; rows=[dedup[k] for k in sorted(dedup)]
    x=np.asarray([r['dt_minus_beta_signed_far_area'] for r in rows],float)
    lag_stats={}
    for lag in (10,20,40,80,120,160,240,320,480,640):
        q=np.asarray([r['lag_contrasts'][str(lag)] for r in rows],float)
        lag_stats[str(lag)]={'mean':float(np.mean(q)),'positive_fraction':float(np.mean(q>0)),'exact_two_sided_signflip_p':exact_signflip_p(q)}
    out={'n':len(rows),'subjects':rows,'primary_signed_far_history':{'mean_dt_minus_beta':float(np.mean(x)),'median_dt_minus_beta':float(np.median(x)),'positive_fraction':float(np.mean(x>0)),'exact_two_sided_signflip_p':exact_signflip_p(x)},'per_lag_dt_minus_beta':lag_stats,'verdict':'The apparent all-six beta > delta/theta result from v1 positive-only area does not survive signed integration. The frozen6 data do not support a clean band-specific history-depth ordering.','guardrail':'v2 is a post-outcome statistical sanity correction because v1 used a positive-clipped area. It prevents a variance/noise floor from masquerading as greater recoverable history.'}
    print(json.dumps(out,indent=2)); p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2))

if __name__=='__main__': main()
