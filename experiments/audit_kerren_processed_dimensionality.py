#!/usr/bin/env python3
"""Small independent audit of Kerrén et al. 2026 processed dimensionality output.

The authors' public MAT contains each participant's remembered/unremembered PCA-elbow
curves, time axis, and the two category trial counts used in each condition.

Question: because PCA is fit across trials and individual participants can have very
unequal remembered vs unsuccessful trial counts, can the reported post-ripple
condition difference be explained by finite-sample count imbalance?

This cannot redo PCA with equalized trial counts because the MAT contains processed
outputs, not trial-level iEEG. It can test the key predictions of a static sample-size
bias:
  * condition dimensionality should covary with the number of trials;
  * remembered-minus-unsuccessful dimensionality should covary with count imbalance;
  * any count-driven offset should also be visible before the ripple;
  * the post-ripple interaction (post condition difference minus pre condition
    difference) should remain after regressing out count imbalance if the effect is
    genuinely event-locked.

No new 'significance window' is searched. Primary post window is the paper's reported
470--840 ms cluster; pre control window is its time-reflected -840-- -470 ms interval.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy import stats

POST=(0.470,0.840)
PRE=(-0.840,-0.470)


def ols_intercept_at_zero(y,x):
    y=np.asarray(y,float); x=np.asarray(x,float)
    X=np.column_stack([np.ones(len(x)),x])
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    resid=y-X@beta; dof=len(y)-2
    s2=np.sum(resid**2)/dof
    cov=s2*np.linalg.inv(X.T@X)
    se=np.sqrt(np.diag(cov)); t=beta/se
    p=2*stats.t.sf(np.abs(t),dof)
    return {'intercept_equal_counts':float(beta[0]),'intercept_se':float(se[0]),'intercept_t':float(t[0]),'intercept_p':float(p[0]),'slope_log_count_ratio':float(beta[1]),'slope_p':float(p[1]),'r2':float(1-np.sum(resid**2)/np.sum((y-y.mean())**2))}


def safepearson(a,b):
    r,p=stats.pearsonr(a,b)
    return {'r':float(r),'p':float(p)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mat');ap.add_argument('--out',required=True);args=ap.parse_args()
    m=loadmat(args.mat,simplify_cells=True)
    perf=m['perf_dimensionality']
    if isinstance(perf,dict): perf=[perf]
    rows=[]
    for i,p in enumerate(perf):
        t=np.asarray(p['time_test'],float).squeeze()
        c=np.asarray(p['correct']['accuracy'],float).squeeze()
        u=np.asarray(p['incorrect']['accuracy'],float).squeeze()
        nc=int(np.sum(np.asarray(p['correct']['trl_num_test'],int)))
        nu=int(np.sum(np.asarray(p['incorrect']['trl_num_test'],int)))
        post=(t>=POST[0])&(t<=POST[1]); pre=(t>=PRE[0])&(t<=PRE[1])
        cp=float(np.mean(c[post])); up=float(np.mean(u[post])); cb=float(np.mean(c[pre])); ub=float(np.mean(u[pre]))
        rows.append({
            'participant':i+1,'n_correct':nc,'n_unsuccessful':nu,'log_count_ratio':float(np.log(nc/nu)),
            'correct_post_dim':cp,'unsuccessful_post_dim':up,'post_diff':cp-up,
            'correct_pre_dim':cb,'unsuccessful_pre_dim':ub,'pre_diff':cb-ub,
            'event_locked_interaction':(cp-up)-(cb-ub),
            'n_channels':int(p['channelcount_test']),
        })
    def v(k):return np.array([r[k] for r in rows],float)
    paired_post=stats.ttest_rel(v('correct_post_dim'),v('unsuccessful_post_dim'))
    paired_pre=stats.ttest_rel(v('correct_pre_dim'),v('unsuccessful_pre_dim'))
    paired_inter=stats.ttest_1samp(v('event_locked_interaction'),0)
    wil_post=stats.wilcoxon(v('correct_post_dim'),v('unsuccessful_post_dim'))
    wil_inter=stats.wilcoxon(v('event_locked_interaction'))
    # Count associations. Spearman added because dimensions are integer-valued before averaging.
    associations={}
    for a,b in [
        ('correct_post_dim','n_correct'),('unsuccessful_post_dim','n_unsuccessful'),
        ('post_diff','log_count_ratio'),('pre_diff','log_count_ratio'),
        ('event_locked_interaction','log_count_ratio'),
    ]:
        pr=safepearson(v(a),v(b)); sr,sp=stats.spearmanr(v(a),v(b)); pr.update(spearman_rho=float(sr),spearman_p=float(sp)); associations[f'{a}_vs_{b}']=pr
    reg_post=ols_intercept_at_zero(v('post_diff'),v('log_count_ratio'))
    reg_inter=ols_intercept_at_zero(v('event_locked_interaction'),v('log_count_ratio'))
    result={
        'source':'Kerren et al 2026 public perf_dimensionality.mat',
        'n_participants':len(rows),'post_window_s':POST,'pre_mirror_window_s':PRE,
        'trial_counts':{
            'correct_mean':float(np.mean(v('n_correct'))),'unsuccessful_mean':float(np.mean(v('n_unsuccessful'))),
            'paired_t_p':float(stats.ttest_rel(v('n_correct'),v('n_unsuccessful')).pvalue),
            'correct_range':[int(v('n_correct').min()),int(v('n_correct').max())],
            'unsuccessful_range':[int(v('n_unsuccessful').min()),int(v('n_unsuccessful').max())],
        },
        'condition_effects':{
            'post_correct_mean':float(np.mean(v('correct_post_dim'))),'post_unsuccessful_mean':float(np.mean(v('unsuccessful_post_dim'))),'post_diff_mean':float(np.mean(v('post_diff'))),'post_paired_t_p':float(paired_post.pvalue),'post_wilcoxon_p':float(wil_post.pvalue),
            'pre_correct_mean':float(np.mean(v('correct_pre_dim'))),'pre_unsuccessful_mean':float(np.mean(v('unsuccessful_pre_dim'))),'pre_diff_mean':float(np.mean(v('pre_diff'))),'pre_paired_t_p':float(paired_pre.pvalue),
            'event_locked_interaction_mean':float(np.mean(v('event_locked_interaction'))),'interaction_t_p':float(paired_inter.pvalue),'interaction_wilcoxon_p':float(wil_inter.pvalue),
        },
        'count_associations':associations,
        'post_diff_regressed_on_log_count_ratio':reg_post,
        'event_locked_interaction_regressed_on_log_count_ratio':reg_inter,
        'participants':rows,
        'guardrails':[
            'This processed-output audit cannot replace an equal-trial-count recomputation from trial-level iEEG.',
            'The 470-840 ms post window is fixed from the published significant cluster; no alternative window was searched.',
            'The mirrored pre-ripple window tests whether a static trial-number bias can explain an event-locked increase.',
            'n=12 makes correlation/regression estimates noisy; absence of correlation is not proof of no finite-sample bias.'
        ]
    }
    print(json.dumps({k:v for k,v in result.items() if k!='participants'},indent=2))
    print('\nPARTICIPANTS')
    for r in rows: print(r)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print('wrote',out)

if __name__=='__main__':main()
