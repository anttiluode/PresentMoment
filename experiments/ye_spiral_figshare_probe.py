#!/usr/bin/env python3
"""Probe the public Figshare metadata for Ye et al. spiral-wave datasets.

This deliberately downloads *metadata only*.  The goal is to discover whether the
visual-motor task deposit exposes small processed files that can be analysed without
pulling the full raw-data archive.

Default article IDs come from the authors' public README:
  25884259  widefield
  25884280  widefield + ephys
  31385869  whisker-evoked widefield
  27850542  visual-motor behavior widefield

No result from this script is neuroscience evidence.  It is a logistics gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

API = "https://api.figshare.com/v2/articles/{article_id}"
DEFAULT_IDS = (25884259, 25884280, 31385869, 27850542)


def get_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "PresentMoment-repro-probe/1.0"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def human_size(n: int | float | None) -> str:
    if n is None:
        return "?"
    n = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024 or unit == "TiB":
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TiB"


def slim(meta: dict) -> dict:
    files = []
    for f in meta.get("files", []):
        files.append(
            {
                "id": f.get("id"),
                "name": f.get("name"),
                "size": f.get("size"),
                "download_url": f.get("download_url"),
                "computed_md5": f.get("computed_md5"),
                "supplied_md5": f.get("supplied_md5"),
            }
        )
    return {
        "id": meta.get("id"),
        "title": meta.get("title"),
        "doi": meta.get("doi"),
        "version": meta.get("version"),
        "defined_type_name": meta.get("defined_type_name"),
        "published_date": meta.get("published_date"),
        "modified_date": meta.get("modified_date"),
        "url_public_html": meta.get("url_public_html"),
        "files": files,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", type=int, action="append", dest="articles")
    ap.add_argument("--out", type=Path, default=Path("results/ye_spiral_figshare_metadata.json"))
    args = ap.parse_args()
    ids = tuple(args.articles) if args.articles else DEFAULT_IDS

    records = []
    for article_id in ids:
        url = API.format(article_id=article_id)
        print(f"\n=== Figshare article {article_id} ===", flush=True)
        meta = get_json(url)
        rec = slim(meta)
        records.append(rec)
        print(f"title: {rec['title']}")
        print(f"version: {rec['version']}  modified: {rec['modified_date']}")
        print(f"files: {len(rec['files'])}")
        total = 0
        for f in rec["files"]:
            size = f.get("size") or 0
            total += size
            print(f"  {f['id']}: {f['name']}  {human_size(size)}")
            print(f"      {f['download_url']}")
        print(f"total listed size: {human_size(total)}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
