#!/usr/bin/env python3
"""Pre-specified independent gate for the repaired RepOD geometry signal.

Dataset: OpenNeuro ds003944, First Episode Psychosis vs Control resting EEG.
This script was frozen BEFORE inspecting any ds003944 EEG outcome with this metric.

Frozen analysis inherited from the RepOD robustness audit:
* only the canonical 19 10-20 electrodes shared with RepOD;
* first 64 s of usable continuous EEG after preprocessing;
* continuous band filtering, discard 2 s each edge -> 60 s analyzed;
* physical standard-10/20 4-nearest-neighbor weighted graph;
* first 6 graph Laplacian modes;
* dominant mode by mean squared projected energy in 0.5-s words;
* cross-band dependence = label-invariant adjusted mutual information (AMI);
* independent Fourier phase randomization per channel preserves each channel's
  magnitude spectrum/autocorrelation but destroys inter-channel timing;
* load-bearing result = observed AMI - mean phase-surrogate AMI.

No parameter is selected using ds003944 outcomes. This 24-person gate uses a subject
list frozen in the workflow from participants.tsv. If the predicted positive
Psychosis-Control excess sign is absent, the gate fails; do not enlarge the sample
in search of significance.

The OpenNeuro export stores anonymous BrainVision names (EEG001...EEG064) in the
.vhdr while BIDS channels.tsv carries the real 10-10 labels, and the resting .vhdr
omits MarkerFile. The adapter below reconstructs only that file-format metadata; it
never changes the frozen metric, subject list, samples, or outcome labels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import mne

from repod_geometry_robustness import graph_modes, seq_fullfilter, ami
from repod_geometric_metric_audit import phase_randomize_channels

# Fixed BIDS channel order from ds003944 *_channels.tsv. This maps the anonymous
# BrainVision Ch1=EEG001 ... Ch64=EEG064 entries to their published labels.
BIDS_64 = [
    "FP1", "FPz", "FP2", "AF7", "AF3", "AF4", "AF6", "F7",
    "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT9", "FT7", "FC5", "FC1", "FC2", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4",
    "C6", "T8", "T10", "TP9", "TP7", "CP3", "CP1", "CP2",
    "CP4", "TP8", "TP10", "P7", "P5", "P3", "P1", "Pz",
    "P2", "P4", "P6", "P8", "PO7", "PO3", "PO4", "PO8",
    "O1", "Oz", "O2", "Iz", "VEOG", "Misc", "ECG", "M2",
]

CANONICAL_19 = [
    "FP1", "FP2", "F7", "F3", "FZ", "F4", "F8",
    "T7", "C3", "CZ", "C4", "T8",
    "P7", "P3", "PZ", "P4", "P8", "O1", "O2",
]
PREPROCESS_FS = 250.0
USE_RAW_S = 70.0  # enough margin for initial filtering + later 64-s metric segment


def _ensure_markerfile(vhdr: Path) -> None:
    """Patch only missing BrainVision MarkerFile metadata for this resting export."""
    text = vhdr.read_text(errors="replace")
    lines = text.splitlines()
    data_file = None
    marker_file = None
    data_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        low = stripped.lower()
        if low.startswith("datafile="):
            data_file = stripped.split("=", 1)[1].strip()
            data_idx = i
        elif low.startswith("markerfile="):
            marker_file = stripped.split("=", 1)[1].strip()

    if data_file is None:
        raise RuntimeError(f"BrainVision header has no DataFile: {vhdr}")

    if marker_file is None:
        marker_file = vhdr.stem + ".vmrk"
        if data_idx is None:
            raise RuntimeError("internal: DataFile line index missing")
        lines.insert(data_idx + 1, f"MarkerFile={marker_file}")
        vhdr.write_text("\n".join(lines) + "\n")
        print(f"inserted missing MarkerFile={marker_file} into {vhdr.name}", flush=True)

    vmrk = vhdr.parent / marker_file
    if not vmrk.exists() or vmrk.stat().st_size == 0:
        vmrk.write_text(
            "Brain Vision Data Exchange Marker File, Version 1.0\n"
            "[Common Infos]\n"
            f"DataFile={data_file}\n"
            "[Marker Infos]\n"
        )
        print(f"created empty resting marker sidecar {vmrk.name}", flush=True)


def read_brainvision(vhdr: Path):
    """Read the public BrainVision data after repairing only missing sidecar metadata."""
    _ensure_markerfile(vhdr)
    return mne.io.read_raw_brainvision(vhdr, preload=True, verbose=False)


def preprocess(vhdr: Path):
    raw = read_brainvision(vhdr)

    # ds003944's BrainVision header anonymizes channel names while BIDS channels.tsv
    # publishes their order. Apply that deterministic adapter before choosing the
    # already-frozen 19-channel subset.
    anonymous = all(c.upper().startswith("EEG") for c in raw.ch_names[:60])
    if anonymous and len(raw.ch_names) >= 64:
        rename = {raw.ch_names[i]: BIDS_64[i] for i in range(64)}
        raw.rename_channels(rename)
        print("mapped EEG001..EEG064 to frozen BIDS channel order", flush=True)

    lookup = {c.upper().replace(" ", ""): c for c in raw.ch_names}
    missing = [c for c in CANONICAL_19 if c not in lookup]
    if missing:
        raise RuntimeError(f"missing canonical channels {missing}; available={raw.ch_names}")
    picks = [lookup[c] for c in CANONICAL_19]
    raw.pick(picks)
    raw.reorder_channels(picks)
    raw.rename_channels({old: new for old, new in zip(raw.ch_names, CANONICAL_19)})
    raw.filter(1.0, 45.0, verbose=False)
    if abs(float(raw.info["sfreq"]) - PREPROCESS_FS) > 1e-6:
        raw.resample(PREPROCESS_FS, verbose=False)

    removed = 0
    try:
        ica = mne.preprocessing.ICA(
            n_components=15, random_state=42, max_iter=500, verbose=False
        )
        ica.fit(raw, verbose=False)
        bad = []
        for fp in ("FP1", "FP2"):
            try:
                idx, _ = ica.find_bads_eog(raw, ch_name=fp, verbose=False)
                bad.extend(idx)
            except Exception:
                pass
        if not bad:
            from scipy.stats import kurtosis
            src = ica.get_sources(raw).get_data()
            bad = np.where(kurtosis(src, axis=1) > 5.0)[0].tolist()[:3]
        bad = sorted(set(bad))
        if bad:
            ica.exclude = bad
            ica.apply(raw, verbose=False)
            removed = len(bad)
    except Exception as exc:
        print(f"ICA failed, continuing exactly as RepOD audit fallback: {exc}", flush=True)

    n = min(int(USE_RAW_S * raw.info["sfreq"]), raw.n_times)
    return raw.get_data()[:, :n], [c.upper() for c in raw.ch_names], float(raw.info["sfreq"]), removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--group", choices=["Control", "Psychosis"], required=True)
    ap.add_argument("--vhdr", type=Path, required=True)
    ap.add_argument("--surrogates", type=int, default=4)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    data, names, sfreq, removed = preprocess(args.vhdr)
    V = graph_modes(names, k=4, n_modes=6)
    obs = ami(seq_fullfilter(data, sfreq, V))
    rng = np.random.default_rng(20260812 + sum(map(ord, args.subject)))
    need = min(int(64 * sfreq), data.shape[1])
    base = data[:, :need]
    sur = []
    for _ in range(args.surrogates):
        xr = phase_randomize_channels(base, rng)
        sur.append(ami(seq_fullfilter(xr, sfreq, V)))
    sm = float(np.mean(sur))
    result = {
        "subject": args.subject,
        "group": args.group,
        "dataset": "OpenNeuro ds003944",
        "metric_frozen_before_outcome": True,
        "channels": CANONICAL_19,
        "graph_k": 4,
        "n_modes": 6,
        "word_s": 0.5,
        "continuous_filtering": True,
        "ica_removed": removed,
        "observed_ami": float(obs),
        "surrogate_ami": list(map(float, sur)),
        "surrogate_mean_ami": sm,
        "excess_ami": float(obs - sm),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
