#!/usr/bin/env python3
"""Inspect the public processed dimensionality MAT from Kerrén et al. 2026.

This is a read-only diagnostic: discover the exact MATLAB structure, extract whatever
participant-level correct/incorrect dimensionality curves and time axes are present,
and report transition-shape summaries without re-fitting the original model.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from scipy.io import loadmat


def desc(x, depth=0, maxdepth=5):
    if depth>maxdepth: return {'type':type(x).__name__,'truncated':True}
    if isinstance(x, dict):
        return {'type':'dict','keys':{str(k):desc(v,depth+1,maxdepth) for k,v in x.items() if not str(k).startswith('__')}}
    if isinstance(x, np.ndarray):
        d={'type':'ndarray','shape':list(x.shape),'dtype':str(x.dtype)}
        if x.dtype==object and x.size<=30:
            d['items']=[desc(v,depth+1,maxdepth) for v in x.flat]
        elif np.issubdtype(x.dtype,np.number) and x.size:
            y=x.astype(float).ravel(); y=y[np.isfinite(y)]
            if len(y): d.update(min=float(y.min()),max=float(y.max()),mean=float(y.mean()))
        return d
    if isinstance(x,(list,tuple)):
        return {'type':type(x).__name__,'len':len(x),'items':[desc(v,depth+1,maxdepth) for v in x[:20]]}
    if hasattr(x,'_fieldnames'):
        return {'type':'mat_struct','fields':{f:desc(getattr(x,f),depth+1,maxdepth) for f in x._fieldnames}}
    if isinstance(x,(str,int,float,bool,np.integer,np.floating)) or x is None:
        try: return {'type':type(x).__name__,'value':x.item() if hasattr(x,'item') else x}
        except Exception: return {'type':type(x).__name__,'repr':repr(x)}
    return {'type':type(x).__name__,'repr':repr(x)[:500]}


def get(obj,*path):
    cur=obj
    for p in path:
        if isinstance(cur,dict): cur=cur[p]
        elif hasattr(cur,p): cur=getattr(cur,p)
        else: return None
    return cur


def as1(x):
    if x is None:return None
    try:return np.asarray(x,dtype=float).squeeze()
    except:return None


def transition_summary(t,curve):
    t=as1(t); y=as1(curve)
    if t is None or y is None or t.ndim!=1 or y.ndim!=1 or len(t)!=len(y): return None
    # pre/post means and broad positive-area centroid relative to pre-ripple mean.
    pre=(t>=-0.8)&(t<0); post=(t>=0)&(t<=1.0)
    base=float(np.nanmean(y[pre])) if pre.any() else float(np.nanmean(y[t<0]))
    dy=y-base
    pos=np.maximum(dy,0)
    m=(t>=0)&(t<=1.0)&np.isfinite(pos)
    centroid=float(np.sum(t[m]*pos[m])/np.sum(pos[m])) if np.sum(pos[m])>0 else None
    peak_i=np.nanargmax(np.where(m,dy,np.nan)) if np.any(m) else None
    return {'pre_mean':base,'post_mean':float(np.nanmean(y[post])),'post_minus_pre':float(np.nanmean(y[post])-base),'positive_area_centroid_s':centroid,'peak_time_s':float(t[peak_i]) if peak_i is not None else None,'peak_delta':float(dy[peak_i]) if peak_i is not None else None}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mat'); ap.add_argument('--out',required=True); args=ap.parse_args()
    raw=loadmat(args.mat,squeeze_me=True,struct_as_record=False)
    print('TOP KEYS', [k for k in raw if not k.startswith('__')])
    structure=desc(raw,maxdepth=4)
    # Also try simplify_cells for easier extraction.
    simple=loadmat(args.mat,simplify_cells=True)
    print('SIMPLIFIED KEYS',[k for k in simple if not k.startswith('__')])
    print(json.dumps(desc(simple,maxdepth=5),indent=2)[:50000])

    result={'source':'Kerren et al 2026 public perf_dimensionality.mat','top_keys':[k for k in simple if not k.startswith('__')],'structure':desc(simple,maxdepth=5)}
    perf=simple.get('perf')
    extracted=[]
    if isinstance(perf,(list,np.ndarray)):
        plist=list(perf) if isinstance(perf,list) else list(np.ravel(perf))
    elif isinstance(perf,dict): plist=[perf]
    else: plist=[]
    for i,p in enumerate(plist):
        if not isinstance(p,dict): continue
        row={'participant_index':i}
        for cond in ('correct','incorrect'):
            c=p.get(cond,{}) if isinstance(p.get(cond,{}),dict) else {}
            row[cond]={}
            for key in ('accuracy','exl_var','trl_num_test'):
                a=as1(c.get(key));
                if a is not None: row[cond][key]={'shape':list(a.shape),'values':a.tolist() if a.size<=20 else None,'mean':float(np.nanmean(a))}
        # likely time field is stored once per participant
        for tk in ('time_test','time_train','time','TOI_ripple'):
            a=as1(p.get(tk))
            if a is not None and a.ndim==1 and a.size>10:
                row[tk]={'n':int(a.size),'min':float(a.min()),'max':float(a.max()),'values':a.tolist()}
        extracted.append(row)
    result['participant_extract']=extracted
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print('wrote',out)

if __name__=='__main__':main()
