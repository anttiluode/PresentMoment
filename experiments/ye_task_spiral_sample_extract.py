#!/usr/bin/env python3
"""Extract the smallest trial-level task spiral file for structure/audit work.

The public task.zip is ~14.2 GiB; ZYE_0088_spirals_task_sort.mat is ~67 MiB and
contains the trial x 141-frame spiral cell array plus T_all.  Pull only that member
through HTTP Range requests so we can decode the real per-trial wave representation
before deciding whether the larger mice are worth fetching.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import json
from remotezip import RemoteZip

ARTICLE=27850542
MEMBER='task/spirals/ZYE_0088_spirals_task_sort.mat'
OUT=Path('results/ye_task_spiral_sample')

req=Request(f'https://api.figshare.com/v2/articles/{ARTICLE}',headers={'User-Agent':'PresentMoment-spiral-sample/1.0'})
with urlopen(req,timeout=60) as r:
    meta=json.loads(r.read().decode())
url=meta['files'][0]['download_url']
OUT.mkdir(parents=True,exist_ok=True)
with RemoteZip(url) as rz:
    z=rz.getinfo(MEMBER)
    print(f'extract {MEMBER}: {z.file_size/1024/1024:.2f} MiB',flush=True)
    dest=OUT/Path(MEMBER).name
    with rz.open(z) as src,dest.open('wb') as dst:
        while True:
            chunk=src.read(1024*1024)
            if not chunk: break
            dst.write(chunk)
print(dest)
