"""Multi-subject real FR1 PTE calibration with anatomy selected before outcome.

This script is the participant-level expansion of the R1022J smoke test.
It intentionally does NOT test the new PresentMoment hypothesis yet.

For one subject/session it:

1. fetches only the public BIDS electrode + bipolar-channel sidecars;
2. selects a same-hemisphere hippocampal bipolar pair whose BOTH contacts are
   hippocampal;
3. selects a same-hemisphere parietal bipolar pair whose BOTH contacts belong to one
   published target class (angular > supramarginal > posterior cingulate > precuneus);
4. makes that choice deterministically from anatomy/labels before opening the PTE result;
5. computes trial-level hippocampus<->parietal PTE direction for delta/theta and beta
   during successful encoding and recall;
6. reports the spectral contrast DI_delta_theta - DI_beta.

The EDF and events file are provided by the workflow. No channel is chosen from its
connectivity result.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

from fr1_pte_calibration import (
    BANDS,
    band_phase,
    load_edf_channels,
    read_events,
    recall_epochs,
    successful_encoding_epochs,
    zscore,
)
from fr1_pte_trial_stats import summarize_trials
from fr1_strict_pair_screen import is_hip, parietal_class, split_pair


S3 = "https://s3.amazonaws.com/openneuro.org"
DATASET = "ds004789"
PAR_PREF = {
    "angular": 0,
    "supramarginal": 1,
    "posterior_cingulate": 2,
    "precuneus": 3,
}


def get_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "PresentMoment-multisubject-PTE/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def remote_tsv(subject: str, session: str, suffix: str) -> list[dict[str, str]]:
    base = f"{S3}/{DATASET}/sub-{subject}/ses-{session}/ieeg"
    name = f"sub-{subject}_ses-{session}_task-FR1_{suffix}"
    return list(csv.DictReader(io.StringIO(get_text(base + "/" + urllib.parse.quote(name))), delimiter="\t"))


def hemi(row: dict[str, str]) -> str | None:
    raw = str(row.get("hemisphere", "")).strip().lower()
    if raw in {"l", "left"}:
        return "L"
    if raw in {"r", "right"}:
        return "R"
    name = str(row.get("name", "")).strip().upper()
    if name.startswith("L"):
        return "L"
    if name.startswith("R"):
        return "R"
    return None


def compact_anatomy(row: dict[str, str]) -> dict[str, str]:
    keys = (
        "name", "hemisphere", "ind.region", "stein.region", "das.region", "wb.region",
        "x", "y", "z",
    )
    return {k: str(row.get(k, "")) for k in keys if str(row.get(k, "")) not in {"", "n/a", "N/A"}}


def select_pair(subject: str, session: str) -> dict[str, object]:
    electrodes = remote_tsv(subject, session, "electrodes.tsv")
    bipolar = remote_tsv(subject, session, "acq-bipolar_channels.tsv")
    by_name = {row.get("name", ""): row for row in electrodes if row.get("name")}

    hip_pairs: list[dict[str, object]] = []
    par_pairs: list[dict[str, object]] = []

    for channel in bipolar:
        name = str(channel.get("name", ""))
        contacts = split_pair(name)
        if contacts is None:
            continue
        a, b = contacts
        if a not in by_name or b not in by_name:
            continue
        ra, rb = by_name[a], by_name[b]
        ha, hb = hemi(ra), hemi(rb)
        if ha is None or hb is None or ha != hb:
            continue

        if is_hip(ra) and is_hip(rb):
            hip_pairs.append(
                {
                    "channel": name,
                    "hemisphere": ha,
                    "a": compact_anatomy(ra),
                    "b": compact_anatomy(rb),
                }
            )

        ca, cb = parietal_class(ra), parietal_class(rb)
        if ca is not None and ca == cb:
            par_pairs.append(
                {
                    "channel": name,
                    "hemisphere": ha,
                    "class": ca,
                    "a": compact_anatomy(ra),
                    "b": compact_anatomy(rb),
                }
            )

    # Candidate combinations must remain within hemisphere. Selection is deterministic
    # and outcome-blind: preferred published cortical class, then lexical channel names.
    combos = [
        (hip, par)
        for hip in hip_pairs
        for par in par_pairs
        if hip["hemisphere"] == par["hemisphere"]
    ]
    if not combos:
        raise RuntimeError(
            f"sub-{subject} ses-{session}: no strict same-hemisphere HIPP/parietal pair"
        )

    combos.sort(
        key=lambda pair: (
            PAR_PREF.get(str(pair[1]["class"]), 99),
            str(pair[0]["hemisphere"]),
            str(pair[0]["channel"]),
            str(pair[1]["channel"]),
        )
    )
    hip, par = combos[0]
    return {
        "hippocampal": hip,
        "parietal": par,
        "n_hippocampal_pairs": len(hip_pairs),
        "n_parietal_pairs": len(par_pairs),
        "n_same_hemi_combinations": len(combos),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--subject", required=True)
    p.add_argument("--session", required=True)
    p.add_argument("--edf", type=Path, required=True)
    p.add_argument("--events", type=Path, required=True)
    p.add_argument("--permutations", type=int, default=20000)
    p.add_argument("--bootstraps", type=int, default=10000)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    selection = select_pair(args.subject, args.session)
    hip_ch = str(selection["hippocampal"]["channel"])
    par_ch = str(selection["parietal"]["channel"])
    print("ANATOMICAL SELECTION (before connectivity result)")
    print(json.dumps(selection, indent=2))

    sfreq, hip_raw, par_raw = load_edf_channels(args.edf, (hip_ch, par_ch))
    hip_raw = zscore(hip_raw)
    par_raw = zscore(par_raw)
    events = read_events(args.events)
    epochs = (
        successful_encoding_epochs(events, sfreq),
        recall_epochs(events, sfreq),
    )
    print(
        f"sfreq={sfreq:g} samples={len(hip_raw)} "
        f"encoding={len(epochs[0].starts)} recall={len(epochs[1].starts)}"
    )

    result: dict[str, object] = {
        "subject": args.subject,
        "session": args.session,
        "selection": selection,
        "sfreq": sfreq,
        "n_samples": int(len(hip_raw)),
        "bands": {},
    }

    for band_i, (band_name, (lo, hi)) in enumerate(BANDS.items()):
        hip_phase = band_phase(hip_raw, sfreq, lo, hi)
        par_phase = band_phase(par_raw, sfreq, lo, hi)
        expected_sign = +1 if band_name == "delta_theta" else -1
        rows = {}
        for epoch_i, epoch_set in enumerate(epochs):
            row = summarize_trials(
                hip_phase,
                par_phase,
                epoch_set,
                expected_sign=expected_sign,
                seed=100_000 + band_i * 1000 + epoch_i,
                permutation_draws=args.permutations,
                bootstrap_draws=args.bootstraps,
            )
            rows[epoch_set.name] = row
            print(f"\n{band_name} / {epoch_set.name}")
            print(json.dumps(row, indent=2))
        result["bands"][band_name] = rows

    contrasts = {}
    for epoch_name in ("successful_encoding", "recall"):
        dt = result["bands"]["delta_theta"][epoch_name]["paired_direction_index_mean"]
        beta = result["bands"]["beta"][epoch_name]["paired_direction_index_mean"]
        contrasts[epoch_name] = {
            "delta_theta_minus_beta_direction_index": float(dt - beta),
            "delta_theta_di": float(dt),
            "beta_di": float(beta),
        }
    result["frequency_contrasts"] = contrasts

    print("\nFREQUENCY CONTRASTS (positive = low band more HIPP-directed than beta)")
    print(json.dumps(contrasts, indent=2))
    print("\nGuardrail: participant-level calibration, not population inference by itself.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
