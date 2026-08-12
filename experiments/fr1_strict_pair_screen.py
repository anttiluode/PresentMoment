"""Metadata-only strict bipolar-pair screen for public FR1 iEEG.

Goal
----
Build an *independently selected* replication pool for the real PTE calibration without
downloading neural signal.

A candidate session must contain:

1. a bipolar channel whose BOTH constituent contacts have an explicit hippocampal
   atlas/region label (hippocampus / CA fields / dentate gyrus / subiculum), and
2. a bipolar channel whose BOTH contacts have the SAME explicit parietal target label
   used by Das & Menon: angular gyrus, supramarginal gyrus, posterior cingulate or
   precuneus.

Important 2026-08-12 correction
-------------------------------
The first version used raw substring matching across every metadata field.  That allowed
``angular`` to match ``parstriangularis`` and therefore admitted frontal contacts into an
`angular` pool.  It also allowed contact names/groups to participate in anatomy matching.

This revision:

* reads anatomy only from explicit region/location fields;
* uses token/phrase-aware regular expressions (``angular`` cannot match
  ``triangularis``);
* excludes contacts whose whole-brain label explicitly says white matter from the
  parietal pool;
* records the exact region fields that caused inclusion.

The script uses only public BIDS TSV metadata from OpenNeuro DS004789.  Atlas labels are
a screening rule, not a substitute for final visual/anatomical QC.

No EDF signal is downloaded.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


S3 = "https://s3.amazonaws.com/openneuro.org"
DATASET = "ds004789"

# Only fields with anatomical meaning may vote on inclusion.  In particular, electrode
# `name` and `group` are intentionally excluded.
REGION_FIELDS = (
    "ind.region",
    "stein.region",
    "das.region",
    "wb.region",
    "location",
    "region",
)

HIP_PATTERNS = (
    re.compile(r"\bhippocamp(?:us|al)?\b", re.I),
    re.compile(r"\bca\s*[1234]\b", re.I),
    re.compile(r"\bdentate(?:\s+gyrus)?\b", re.I),
    re.compile(r"\bdg\b", re.I),
    re.compile(r"\bsubiculum\b|\bsubicular\b|\bsub\b", re.I),
)

PARIETAL_PATTERNS = {
    "angular": (
        re.compile(r"\bangular(?:\s+gyrus)?\b", re.I),
        re.compile(r"\bAG\b"),
    ),
    "supramarginal": (
        re.compile(r"\bsupramarginal(?:\s+gyrus)?\b", re.I),
        re.compile(r"\bSMG\b"),
    ),
    "precuneus": (
        re.compile(r"\bprecuneus\b", re.I),
        re.compile(r"\bPCU\b"),
    ),
    "posterior_cingulate": (
        re.compile(r"\bposterior\s+cingulate(?:\s+(?:cortex|gyrus))?\b", re.I),
        re.compile(r"\bPCC\b"),
    ),
}

WHITE_MATTER_RE = re.compile(r"\bwhite\s+matter\b", re.I)


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "PresentMoment-strict-pair-screen/2"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def list_objects(prefix: str, *, delimiter: str | None = None, max_keys: int = 1000) -> dict:
    params = {"list-type": "2", "prefix": prefix, "max-keys": str(max_keys)}
    if delimiter:
        params["delimiter"] = delimiter
    root = ET.fromstring(get(S3 + "?" + urllib.parse.urlencode(params)))
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    keys = []
    for node in root.findall("s3:Contents", ns):
        key = node.findtext("s3:Key", namespaces=ns)
        size = node.findtext("s3:Size", namespaces=ns)
        if key:
            keys.append((key, int(size or 0)))
    prefixes = [
        n.text for n in root.findall("s3:CommonPrefixes/s3:Prefix", ns) if n.text
    ]
    truncated = root.findtext("s3:IsTruncated", default="false", namespaces=ns) == "true"
    return {"keys": keys, "prefixes": prefixes, "truncated": truncated}


def object_url(key: str) -> str:
    return S3 + "/" + urllib.parse.quote(key, safe="/")


def read_tsv(key: str) -> list[dict[str, str]]:
    text = get(object_url(key)).decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def region_values(row: dict[str, str]) -> dict[str, str]:
    """Return nonempty anatomy fields only; names/groups cannot vote on anatomy."""
    out: dict[str, str] = {}
    for field in REGION_FIELDS:
        value = str(row.get(field, "")).strip()
        if value and value.lower() not in {"n/a", "na", "nan", "unknown", "none"}:
            out[field] = value
    return out


def anatomy_text(row: dict[str, str]) -> str:
    """Human-readable explicit anatomy only (kept for logs/backward-compatible imports)."""
    vals = region_values(row)
    return " | ".join(f"{k}={v}" for k, v in vals.items())


def _matches_any(values: dict[str, str], patterns: tuple[re.Pattern, ...]) -> bool:
    return any(pattern.search(value) for value in values.values() for pattern in patterns)


def is_white_matter(row: dict[str, str]) -> bool:
    # `wb.region` is the most explicit whole-brain tissue label in this release.  If it
    # says White Matter, reject the contact from the cortical target pool even if a
    # surface atlas projects it onto a nearby gyrus.
    wb = str(row.get("wb.region", "")).strip()
    return bool(WHITE_MATTER_RE.search(wb))


def is_hip(row: dict[str, str]) -> bool:
    return _matches_any(region_values(row), HIP_PATTERNS)


def parietal_class(row: dict[str, str]) -> str | None:
    if is_white_matter(row):
        return None
    values = region_values(row)
    for cls, patterns in PARIETAL_PATTERNS.items():
        if _matches_any(values, patterns):
            return cls
    return None


def split_pair(name: str) -> tuple[str, str] | None:
    # Electrode names in this BIDS export are simple CONTACT1-CONTACT2 pairs.
    parts = name.split("-")
    if len(parts) != 2 or not all(parts):
        return None
    return parts[0], parts[1]


def pair_candidates(electrodes: list[dict[str, str]], bipolar: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    by_name = {row.get("name", ""): row for row in electrodes if row.get("name")}
    hip_pairs = []
    par_pairs = []

    for channel in bipolar:
        name = channel.get("name", "")
        contacts = split_pair(name)
        if contacts is None:
            continue
        a, b = contacts
        if a not in by_name or b not in by_name:
            continue
        ra, rb = by_name[a], by_name[b]

        if is_hip(ra) and is_hip(rb):
            hip_pairs.append(
                {
                    "channel": name,
                    "group": channel.get("group", ""),
                    "contact_a": {
                        "name": a,
                        "anatomy": region_values(ra),
                    },
                    "contact_b": {
                        "name": b,
                        "anatomy": region_values(rb),
                    },
                }
            )

        ca, cb = parietal_class(ra), parietal_class(rb)
        if ca is not None and ca == cb:
            par_pairs.append(
                {
                    "channel": name,
                    "class": ca,
                    "group": channel.get("group", ""),
                    "contact_a": {
                        "name": a,
                        "anatomy": region_values(ra),
                    },
                    "contact_b": {
                        "name": b,
                        "anatomy": region_values(rb),
                    },
                }
            )

    return hip_pairs, par_pairs


def session_prefix_from_key(key: str) -> str:
    # ds004789/sub-X/ses-Y/ieeg/file -> ds004789/sub-X/ses-Y/
    parts = key.split("/")
    if len(parts) < 4:
        return ""
    return "/".join(parts[:3]) + "/"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max-subjects", type=int, default=100)
    p.add_argument("--max-candidates", type=int, default=30)
    p.add_argument("--out", default="results/fr1-strict-pair-screen.json")
    args = p.parse_args()

    # Explicit regression tests for the bug that triggered this revision.
    assert parietal_class({"ind.region": "parstriangularis"}) is None
    assert parietal_class({"ind.region": "angular"}) == "angular"
    assert parietal_class({"ind.region": "angular", "wb.region": "Left Cerebral White Matter"}) is None
    assert is_hip({"stein.region": "Left CA1"})

    root = list_objects(f"{DATASET}/", delimiter="/")
    subjects = sorted(
        prefix for prefix in root["prefixes"]
        if re.search(r"/sub-[^/]+/$", prefix)
    )[: args.max_subjects]

    candidates = []
    inspected_sessions = 0
    for subject_prefix in subjects:
        listing = list_objects(subject_prefix, max_keys=1000)
        keys = listing["keys"]
        sessions: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for key, size in keys:
            sp = session_prefix_from_key(key)
            if sp:
                sessions[sp].append((key, size))

        for session_prefix, session_objects in sorted(sessions.items()):
            electrode_files = [k for k, _ in session_objects if k.endswith("electrodes.tsv")]
            bipolar_files = [k for k, _ in session_objects if k.endswith("acq-bipolar_channels.tsv")]
            edf_files = [(k, s) for k, s in session_objects if k.endswith("acq-bipolar_ieeg.edf")]
            event_files = [k for k, _ in session_objects if k.endswith("events.tsv")]
            if not (electrode_files and bipolar_files and edf_files and event_files):
                continue
            inspected_sessions += 1

            electrodes = read_tsv(electrode_files[0])
            bipolar = read_tsv(bipolar_files[0])
            hip_pairs, par_pairs = pair_candidates(electrodes, bipolar)
            if not (hip_pairs and par_pairs):
                continue

            candidate = {
                "subject": session_prefix.split("/")[1],
                "session": session_prefix.split("/")[2],
                "hippocampal_pairs": hip_pairs,
                "parietal_pairs": par_pairs,
                "bipolar_edf": edf_files[0][0],
                "bipolar_edf_mib": edf_files[0][1] / (1024 ** 2),
                "events_tsv": event_files[0],
                "electrodes_tsv": electrode_files[0],
                "bipolar_channels_tsv": bipolar_files[0],
            }
            candidates.append(candidate)
            print(
                f"{candidate['subject']} {candidate['session']}: "
                f"hip={len(hip_pairs)} par={len(par_pairs)} "
                f"edf={candidate['bipolar_edf_mib']:.1f} MiB"
            )
            print("  HIP:", [x["channel"] for x in hip_pairs[:6]])
            print("  PAR:", [(x["channel"], x["class"]) for x in par_pairs[:8]])

            if len(candidates) >= args.max_candidates:
                break
        if len(candidates) >= args.max_candidates:
            break

    payload = {
        "dataset": DATASET,
        "screen_version": "token-exact-gray-matter-v2",
        "subjects_requested": args.max_subjects,
        "sessions_inspected": inspected_sessions,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\ninspected_sessions={inspected_sessions} strict_candidates={len(candidates)}")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
