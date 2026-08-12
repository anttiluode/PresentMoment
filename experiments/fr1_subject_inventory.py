"""Targeted metadata inventory for one FR1 iEEG subject.

No neural signal is downloaded. This prints exact recording sizes, event schema and
anatomically relevant electrode/channel rows so a later GitHub Actions analysis can
select one manageable recording without guessing.

Default subject: sub-R1022J, chosen from the sidecar-only screen because its single FR1
session contains left hippocampal (CA1/DG/Hippocampus) and left parietal/cortical labels.

Run:
    python experiments/fr1_subject_inventory.py
"""
from __future__ import annotations

import csv
import io
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter


S3 = "https://s3.amazonaws.com/openneuro.org"
DATASET = "ds004789"
SUBJECT = "sub-R1022J"

HIP_WORDS = ("hipp", "ca1", "ca2", "ca3", "dentate", "dg", "subiculum")
PARIETAL_WORDS = (
    "pariet", "angular", "precune", "supramarg", "postcentral", "paracentral",
)
TARGET_GROUPS = {"LB", "LC", "LH", "LAIL", "LPSL", "LSS"}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "PresentMoment-FR1-inventory/2"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def object_url(key: str) -> str:
    return S3 + "/" + urllib.parse.quote(key, safe="/")


def list_objects(prefix: str) -> list[dict[str, object]]:
    params = urllib.parse.urlencode({"list-type": "2", "prefix": prefix, "max-keys": "1000"})
    root = ET.fromstring(get(S3 + "?" + params))
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    out = []
    for node in root.findall("s3:Contents", ns):
        key = node.findtext("s3:Key", namespaces=ns)
        size = node.findtext("s3:Size", namespaces=ns)
        if key:
            out.append({"key": key, "size": int(size or 0)})
    return out


def read_tsv(key: str) -> list[dict[str, str]]:
    text = get(object_url(key)).decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def row_text(row: dict[str, str]) -> str:
    return " | ".join(str(v) for v in row.values() if v and str(v).lower() not in {"n/a", "nan", "unknown"})


def relevant(rows: list[dict[str, str]], words: tuple[str, ...]) -> list[dict[str, str]]:
    return [row for row in rows if any(w in row_text(row).lower() for w in words)]


def compact(row: dict[str, str]) -> dict[str, str]:
    preferred = (
        "name", "group", "type", "hemisphere", "ind.region", "stein.region",
        "das.region", "wb.region", "x", "y", "z", "tal.x", "tal.y", "tal.z",
        "status", "status_description", "sampling_frequency", "reference",
    )
    return {k: row[k] for k in preferred if k in row and row[k] not in ("", "n/a", "N/A")}


def main() -> None:
    prefix = f"{DATASET}/{SUBJECT}/"
    objects = list_objects(prefix)
    print(f"PresentMoment FR1 inventory: {SUBJECT}")
    print(f"objects={len(objects)}")
    print()

    for obj in objects:
        key = str(obj["key"])
        size = int(obj["size"])
        if key.endswith((".edf", ".tsv", ".json")):
            print(f"{size / (1024**2):9.2f} MiB  {key}")

    electrode_files = [str(o["key"]) for o in objects if str(o["key"]).endswith("electrodes.tsv")]
    mono_files = [str(o["key"]) for o in objects if str(o["key"]).endswith("acq-monopolar_channels.tsv")]
    bipolar_files = [str(o["key"]) for o in objects if str(o["key"]).endswith("acq-bipolar_channels.tsv")]
    event_files = [str(o["key"]) for o in objects if str(o["key"]).endswith("events.tsv")]

    if not (electrode_files and mono_files and bipolar_files and event_files):
        raise RuntimeError("expected electrode/channel/event sidecars")

    electrodes = read_tsv(electrode_files[0])
    mono = read_tsv(mono_files[0])
    bipolar = read_tsv(bipolar_files[0])
    events = read_tsv(event_files[0])

    hip = relevant(electrodes, HIP_WORDS)
    par = relevant(electrodes, PARIETAL_WORDS)

    print("\nELECTRODE COLUMNS")
    print(list(electrodes[0].keys()) if electrodes else [])
    print(f"electrodes={len(electrodes)} hippocampal_matches={len(hip)} parietal_matches={len(par)}")

    print("\nHIPPOCAMPAL CANDIDATES")
    for row in hip:
        print(json.dumps(compact(row), sort_keys=True))

    print("\nPARIETAL CANDIDATES")
    for row in par:
        print(json.dumps(compact(row), sort_keys=True))

    channel_by_name = {row.get("name", ""): row for row in mono}
    chosen_names = [row.get("name", "") for row in hip + par if row.get("name")]
    print("\nMATCHING MONOPOLAR CHANNEL ROWS")
    matched = 0
    for name in chosen_names:
        if name in channel_by_name:
            print(json.dumps(compact(channel_by_name[name]), sort_keys=True))
            matched += 1
    print(f"matched={matched}/{len(chosen_names)} electrode names")

    print("\nBIPOLAR CHANNEL COLUMNS")
    print(list(bipolar[0].keys()) if bipolar else [])
    print(f"bipolar_channels={len(bipolar)}")
    print("\nTARGET-GROUP BIPOLAR CHANNELS")
    for row in bipolar:
        name = row.get("name", "")
        group = row.get("group", "")
        # Some BIDS exports retain group; others encode source contacts in channel name.
        if group in TARGET_GROUPS or any(name.startswith(g) for g in TARGET_GROUPS):
            print(json.dumps(compact(row), sort_keys=True))

    print("\nEVENT SCHEMA")
    print(list(events[0].keys()) if events else [])
    print(f"events={len(events)}")
    for column in ("trial_type", "type", "event_type", "item_name", "recalled", "list", "mstime"):
        if events and column in events[0]:
            counts = Counter(row.get(column, "") for row in events)
            print(f"{column}: {counts.most_common(12)}")

    print("\nFIRST 12 EVENTS")
    for row in events[:12]:
        print(json.dumps(row, sort_keys=True))


if __name__ == "__main__":
    main()
