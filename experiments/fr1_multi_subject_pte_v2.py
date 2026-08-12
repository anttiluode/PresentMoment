"""Robust wrapper for fr1_multi_subject_pte.py.

OpenNeuro/BIDS sidecars are not all stored at the same entity/path level.  Rather than
constructing an `electrodes.tsv` or `channels.tsv` URL from assumptions, this wrapper
lists the selected subject/session prefix in the public OpenNeuro S3 bucket and resolves
the unique key by suffix.  It then monkey-patches the original analysis module's
`remote_tsv` helper and runs the unchanged, outcome-blind PTE analysis.

This keeps the six-subject cohort and anatomical selection rules frozen while removing
only data-layout assumptions.
"""
from __future__ import annotations

import csv
import functools
import io
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import fr1_multi_subject_pte as analysis


S3_LIST = "https://s3.amazonaws.com/openneuro.org"
DATASET = "ds004789"


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "PresentMoment-multisubject-PTE/3"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


@functools.lru_cache(maxsize=None)
def session_keys(subject: str, session: str) -> tuple[str, ...]:
    prefix = f"{DATASET}/sub-{subject}/ses-{session}/"
    params = urllib.parse.urlencode(
        {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
    )
    root = ET.fromstring(get_bytes(S3_LIST + "?" + params))
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    keys = tuple(
        node.text
        for node in root.findall("s3:Contents/s3:Key", ns)
        if node.text
    )
    if not keys:
        raise RuntimeError(f"no S3 keys found for {prefix}")
    return keys


def resolve_sidecar(subject: str, session: str, suffix: str) -> str:
    keys = session_keys(subject, session)
    matches = [key for key in keys if key.endswith(suffix)]

    # When a generic suffix could match multiple acquisitions, prefer FR1, then bipolar.
    if len(matches) > 1:
        fr1 = [key for key in matches if "task-FR1" in key]
        if fr1:
            matches = fr1
    if len(matches) > 1 and "channels.tsv" in suffix:
        bipolar = [key for key in matches if "acq-bipolar" in key]
        if bipolar:
            matches = bipolar

    if len(matches) != 1:
        raise RuntimeError(
            f"expected one {suffix!r} key for sub-{subject} ses-{session}, got {matches}"
        )
    return matches[0]


def robust_remote_tsv(subject: str, session: str, suffix: str) -> list[dict[str, str]]:
    key = resolve_sidecar(subject, session, suffix)
    print(f"resolved sidecar {suffix}: {key}")
    url = S3_LIST + "/" + urllib.parse.quote(key, safe="/")
    text = get_bytes(url).decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def main() -> None:
    analysis.remote_tsv = robust_remote_tsv
    analysis.main()


if __name__ == "__main__":
    main()
