#!/usr/bin/env python3
"""Index Ye et al. task.zip remotely and extract only small processed task files.

The Figshare deposit is a single ~14 GiB ZIP.  Downloading it wholesale is unnecessary
for the first audit: ZIP central directories and selected members can be read with HTTP
Range requests.  This script uses `remotezip` and enforces both per-file and total caps.

Default selection targets the files used by the authors' behavioral phase plots:
  - task/task_outcome/*   (trial outcome + precomputed band phase/amplitude)
  - task/sessions/*       (session metadata)

It deliberately does NOT fetch task_svd, videos, rfmap, or raw block data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

from remotezip import RemoteZip

FIGSHARE_ARTICLE = 27850542
API = f"https://api.figshare.com/v2/articles/{FIGSHARE_ARTICLE}"


def get_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "PresentMoment-remotezip/1.0"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def wanted(name: str) -> bool:
    p = name.replace("\\", "/").lower()
    return "/task_outcome/" in p or "/sessions/" in p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("results/ye_task_subset"))
    ap.add_argument("--manifest", type=Path, default=Path("results/ye_task_zip_manifest.json"))
    ap.add_argument("--max-file-mb", type=float, default=80.0)
    ap.add_argument("--max-total-mb", type=float, default=250.0)
    args = ap.parse_args()

    meta = get_json(API)
    files = meta.get("files", [])
    if len(files) != 1:
        raise RuntimeError(f"Expected one deposited ZIP, got {len(files)} files")
    url = files[0]["download_url"]
    print(f"remote ZIP: {files[0]['name']} size={files[0]['size']} url={url}", flush=True)

    with RemoteZip(url) as rz:
        infos = rz.infolist()
        print(f"ZIP entries: {len(infos)}", flush=True)
        manifest = [
            {
                "filename": z.filename,
                "file_size": z.file_size,
                "compress_size": z.compress_size,
                "crc": z.CRC,
            }
            for z in infos
        ]
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        matches = [z for z in infos if wanted(z.filename) and not z.is_dir()]
        print(f"matching processed/session entries: {len(matches)}")
        for z in matches:
            print(f"  {z.filename}  {z.file_size/1024/1024:.2f} MiB")

        max_file = int(args.max_file_mb * 1024 * 1024)
        max_total = int(args.max_total_mb * 1024 * 1024)
        selected = [z for z in matches if z.file_size <= max_file]
        total = sum(z.file_size for z in selected)
        print(f"selected under per-file cap: {len(selected)} entries, {total/1024/1024:.2f} MiB total")
        if total > max_total:
            raise RuntimeError(
                f"Selected subset {total/1024/1024:.1f} MiB exceeds hard total cap {args.max_total_mb:.1f} MiB"
            )

        args.out.mkdir(parents=True, exist_ok=True)
        index = []
        for z in selected:
            # Strip archive parent directories but retain enough hierarchy to avoid collisions.
            parts = Path(z.filename).parts
            try:
                task_i = [p.lower() for p in parts].index("task")
                rel = Path(*parts[task_i:])
            except ValueError:
                rel = Path(*parts[-2:])
            dest = args.out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"extract {z.filename} -> {dest}", flush=True)
            with rz.open(z) as src, dest.open("wb") as dst:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    dst.write(chunk)
            index.append({"archive": z.filename, "local": str(dest), "size": z.file_size})

        (args.out / "subset_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
        print(f"extracted {len(index)} files", flush=True)


if __name__ == "__main__":
    main()
