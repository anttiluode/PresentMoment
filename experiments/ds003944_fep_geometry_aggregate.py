#!/usr/bin/env python3
"""Aggregate the frozen 24-person ds003944 independent replication gate."""
from __future__ import annotations
import argparse, glob, json, math
from pathlib import Path
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--out',required=True); args=ap.parse_args()
    files=glob.glob(str(Path(args.root)/'**'/'*.json'),recursive=True)
    rows=[]
    for f in files:
        try:
            r=json.loads(Path(f).read_text())
            if r.get('dataset')=='OpenNeuro ds003944': rows.append(r)
        except Exception: pass
    rows=sorted(rows,key=lambda r:r['subject'])
    if len(rows)!=24: raise RuntimeError(f'expected frozen 24 subjects, found {len(rows)}')
    con=np.array([r['excess_ami'] for r in rows if r['group']=='Control'],float)
    psy=np.array([r['excess_ami'] for r in rows if r['group']=='Psychosis'],float)
    if len(con)!=12 or len(psy)!=12: raise RuntimeError(f'expected 12/12, got {len(con)}/{len(psy)}')
    t,p2=ttest_ind(con,psy,equal_var=True)
    pooled=math.sqrt(((len(con)-1)*con.var(ddof=1)+(len(psy)-1)*psy.var(ddof=1))/(len(con)+len(psy)-2))
    d=(psy.mean()-con.mean())/pooled if pooled else float('nan')
    u,pmw=mannwhitneyu(psy,con,alternative='two-sided')
    # Pre-registered directional question inherited from RepOD: Psychosis > Control.
    # One-sided t p is derived from the two-sided symmetric t test only when sign matches.
    p_one=float(p2/2 if psy.mean()>con.mean() else 1-p2/2)
    result={
        'dataset':'OpenNeuro ds003944',
        'gate_subjects':24,'n_control':12,'n_psychosis':12,
        'selection':'first 12 lexicographic non-A Control and first 12 lexicographic non-A Psychosis IDs from participants.tsv, frozen before EEG outcomes',
        'metric':'continuous-filter physical 10-20 k=4, 6 modes, energy winner, cross-band AMI, observed-minus-independent-channel Fourier-phase-surrogate',
        'prediction_frozen_before_outcome':'Psychosis excess_ami > Control excess_ami',
        'control_mean_excess_ami':float(con.mean()),'psychosis_mean_excess_ami':float(psy.mean()),
        'psychosis_minus_control':float(psy.mean()-con.mean()),
        'cohen_d_psychosis_minus_control':float(d),'student_t_control_minus_psychosis':float(t),
        'two_sided_t_p':float(p2),'pre_registered_one_sided_t_p':p_one,
        'mann_whitney_u_psychosis_first':float(u),'mann_whitney_two_sided_p':float(pmw),
        'predicted_sign_observed':bool(psy.mean()>con.mean()),
        'gate_pass_definition':'Predicted sign must be positive. Statistical significance is reported, not required to decide whether to scale; if sign is absent, do not enlarge cohort.',
        'subjects':rows,
        'guardrail':'First-episode psychosis is not identical to chronic schizophrenia. A same-sign result would support generalization to psychosis-spectrum EEG dynamics, not a schizophrenia-specific biomarker.'
    }
    print(json.dumps({k:v for k,v in result.items() if k!='subjects'},indent=2))
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2))

if __name__=='__main__': main()
