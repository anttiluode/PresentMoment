"""Metadata-only probe of the public FR1 iEEG corpus via EEGDash.

Purpose
-------
Before downloading any of the ~576 GB DS004789 corpus, ask whether EEGDash exposes
enough BIDS metadata to select a small set of recordings for a receiver/directionality
analysis.

This script intentionally downloads no neural signal.  It only queries EEGDash's
public metadata API and prints a compact inventory of record fields and subjects.

Run:
    python experiments/eegdash_fr1_metadata_probe.py
"""
from __future__ import annotations

import json
from collections import Counter

from eegdash import EEGDash


DATASET = "ds004789"


def simplify(obj):
    if isinstance(obj, dict):
        return {str(k): simplify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [simplify(v) for v in obj]
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    return repr(obj)


def pick(record: dict, names: tuple[str, ...]):
    for name in names:
        if name in record:
            return record[name]
    return None


def main() -> None:
    client = EEGDash()
    records = client.find(dataset=DATASET)

    print("PresentMoment: EEGDash FR1 metadata probe")
    print(f"dataset={DATASET} records={len(records)}")
    if not records:
        raise RuntimeError("EEGDash returned no DS004789 records")

    records = [dict(r) for r in records]
    keys = sorted({k for r in records for k in r.keys()})
    print("record keys:")
    print("  " + "\n  ".join(keys))

    subjects = [str(pick(r, ("subject", "sub"))) for r in records]
    print(f"unique subjects={len(set(subjects))}")
    print("record counts for first 20 subjects:")
    for subject, count in sorted(Counter(subjects).items())[:20]:
        print(f"  {subject}: {count}")

    print("\nfirst 3 records (selected fields):")
    candidate_names = (
        "dataset", "subject", "session", "run", "task", "modality",
        "sampling_frequency", "sfreq", "n_channels", "duration", "path",
        "file_path", "bids_path", "recording_id", "datatype", "channel_types",
    )
    for i, record in enumerate(records[:3]):
        selected = {k: record.get(k) for k in candidate_names if k in record}
        print(f"record {i}:")
        print(json.dumps(simplify(selected), indent=2, sort_keys=True))

    print("\nfirst record full metadata:")
    print(json.dumps(simplify(records[0]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
