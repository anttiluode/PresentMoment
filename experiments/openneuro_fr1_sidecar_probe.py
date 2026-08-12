"""Sidecar-only probe of OpenNeuro DS004789 (FR1) via its public S3 bucket.

No iEEG signal is downloaded.  The script lists the BIDS tree and fetches only small
TSV/JSON sidecars so we can answer a practical question before attempting a real-data
analysis:

    Which subjects have annotations/contact names consistent with hippocampal AND
    cortical coverage, and what are the exact recording/event file paths?

This bypasses EEGDash's catalog layer and talks to the canonical public OpenNeuro
storage.  It is intentionally conservative about anatomy: string matches are candidate
selection only, not final neuroanatomical labels.

Run:
    python experiments/openneuro_fr1_sidecar_probe.py
"""
from __future__ import annotations

import csv
import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter


BUCKET = "https://openneuro.org.s3.amazonaws.com/"
DATASET = "ds004789"
MAX_SUBJECTS = 30

HIPPO_WORDS = (
    "hipp", "ca1", "ca2", "ca3", "dentate", "dg", "subiculum", "subic",
)
CORTEX_WORDS = (
    "frontal", "pariet", "temporal", "occip", "cing", "precentral", "postcentral",
    "angular", "supramarg", "precuneus", "fusiform", "orbitofrontal", "motor",
)


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "PresentMoment-sidecar-probe/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def list_objects(prefix: str, *, delimiter: str | None = None, max_keys: int = 1000) -> dict:
    params = {"list-type": "2", "prefix": prefix, "max-keys": str(max_keys)}
    if delimiter is not None:
        params["delimiter"] = delimiter
    url = BUCKET + "?" + urllib.parse.urlencode(params)
    root = ET.fromstring(get_bytes(url))
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    keys = [n.text for n in root.findall("s3:Contents/s3:Key", ns) if n.text]
    prefixes = [n.text for n in root.findall("s3:CommonPrefixes/s3:Prefix", ns) if n.text]
    return {
        "keys": keys,
        "prefixes": prefixes,
        "truncated": (root.findtext("s3:IsTruncated", default="false", namespaces=ns) == "true"),
    }


def object_url(key: str) -> str:
    return BUCKET + urllib.parse.quote(key, safe="/")


def fetch_text(key: str) -> str:
    return get_bytes(object_url(key)).decode("utf-8", errors="replace")


def tsv_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def anatomical_strings(rows: list[dict[str, str]]) -> list[str]:
    out = []
    for row in rows:
        for key, value in row.items():
            k = (key or "").lower()
            if any(token in k for token in ("region", "anat", "label", "location", "name", "desikan")):
                if value and value.lower() not in {"n/a", "na", "nan", "unknown"}:
                    out.append(value)
    return out


def candidate_flags(strings: list[str]) -> tuple[bool, bool, list[str], list[str]]:
    norm = [s.lower() for s in strings]
    hip = sorted({s for s in strings if any(w in s.lower() for w in HIPPO_WORDS)})
    ctx = sorted({s for s in strings if any(w in s.lower() for w in CORTEX_WORDS)})
    return bool(hip), bool(ctx), hip[:12], ctx[:12]


def main() -> None:
    print("PresentMoment: OpenNeuro FR1 sidecar-only probe")
    print(f"bucket={BUCKET} dataset={DATASET}")

    root = list_objects(f"{DATASET}/", delimiter="/")
    subjects = sorted(p for p in root["prefixes"] if re.search(r"/sub-[^/]+/$", p))
    print(f"subject prefixes visible={len(subjects)} truncated={root['truncated']}")
    print("first subjects:", subjects[:10])

    candidates = []
    inspected = 0
    for subject_prefix in subjects[:MAX_SUBJECTS]:
        # A subject has only hundreds of small+large keys, usually below 1000. Listing
        # object names transfers metadata only; no object bodies are downloaded.
        listing = list_objects(subject_prefix, max_keys=1000)
        keys = listing["keys"]
        sidecar_keys = [
            k for k in keys
            if k.endswith(("electrodes.tsv", "channels.tsv", "coordsystem.json", "events.tsv"))
        ]
        anatomical_keys = [k for k in sidecar_keys if k.endswith("electrodes.tsv")]

        strings: list[str] = []
        electrode_columns: list[str] = []
        electrode_row_count = 0
        for key in anatomical_keys:
            rows = tsv_rows(fetch_text(key))
            electrode_row_count += len(rows)
            if rows:
                electrode_columns.extend(rows[0].keys())
            strings.extend(anatomical_strings(rows))

        has_hip, has_ctx, hip_examples, ctx_examples = candidate_flags(strings)
        record_keys = [k for k in keys if k.endswith((".edf", ".vhdr", ".eeg", ".set"))]
        event_keys = [k for k in keys if k.endswith("events.tsv")]
        channel_keys = [k for k in keys if k.endswith("channels.tsv")]

        inspected += 1
        subject = subject_prefix.rstrip("/").split("/")[-1]
        print(
            f"{subject}: keys={len(keys)} electrodes={electrode_row_count} "
            f"recordings={len(record_keys)} events={len(event_keys)} "
            f"hip?={has_hip} cortex?={has_ctx}"
        )

        if has_hip and has_ctx:
            candidates.append(
                {
                    "subject": subject,
                    "hippocampal_examples": hip_examples,
                    "cortical_examples": ctx_examples,
                    "electrode_columns": sorted(set(electrode_columns)),
                    "electrode_files": anatomical_keys,
                    "channel_files": channel_keys[:5],
                    "event_files": event_keys[:5],
                    "recording_files": record_keys[:5],
                    "listing_truncated": listing["truncated"],
                }
            )

    print()
    print(f"inspected={inspected} candidate subjects={len(candidates)}")
    print(json.dumps(candidates[:10], indent=2))

    if candidates:
        print("\nCandidate-selection caveat:")
        print("  anatomical string matching is only a download-selection heuristic;")
        print("  any real analysis must use the dataset's coordinate/region metadata explicitly.")
    else:
        print("\nNo joint hippocampal+cortical candidate found in this first metadata slice.")
        print("That does NOT mean the corpus lacks them; inspect more prefixes or the annotation schema.")


if __name__ == "__main__":
    main()
