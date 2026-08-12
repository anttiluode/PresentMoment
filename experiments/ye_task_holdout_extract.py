#!/usr/bin/env python3
"""Extract only the unopened 2-8 Hz task files for ZYE_0085 and ZYE_0091.

These two subjects are held out from the first past-only accessibility prototype,
which was inspected on ZYE_0088 and ZYE_0090.  This script exists so the remaining
subjects can be evaluated without downloading the 14.2 GiB task archive.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import json
from remotezip import RemoteZip

ARTICLE=27850542
TARGETS={
    'task/task_outcome/ZYE_0085_task_freq_to8Hz.mat',
    'task/task_outcome/ZYE_0091_task_freq_to8Hz.mat',
}
OUT=Path('results/ye_task_holdout')

req=Request(f'https://api.figshare.com/v2/articles/{ARTICLE}',headers={'User-Agent':'PresentMoment-holdout/1.0'})
with urlopen(req,timeout=60) as r:
    meta=json.loads(r.read().decode())
url=meta['files'][0]['download_url']
OUT.mkdir(parents=True,exist_ok=True)
with RemoteZip(url) as rz:
    by_name={z.filename:z for z in rz.infolist()}
    missing=TARGETS-set(by_name)
    if missing:
        raise RuntimeError(f'missing members: {sorted(missing)}')
    for name in sorted(TARGETS):
        z=by_name[name]
        print(f'extract {name}: {z.file_size/1024/1024:.2f} MiB',flush=True)
        dest=OUT/Path(name).name
        with rz.open(z) as src,dest.open('wb') as dst:
            while True:
                chunk=src.read(1024*1024)
                if not chunk: break
                dst.write(chunk)
print('done')
