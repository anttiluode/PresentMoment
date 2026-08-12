"""Real human iEEG calibration: hippocampus <-> angular gyrus directed phase transfer.

This is deliberately a replication/calibration smoke test before asking any new
PresentMoment question.

Dataset
-------
OpenNeuro DS004789 (UPENN-RAM FR1), subject R1022J session 0, bipolar EDF.
The metadata-only screen identified an unusually clean pair:

    hippocampus : LB2-LB3   (Left DG <-> Left CA1)
    angular     : LH11-LH12 (Left angular gyrus <-> Left angular gyrus)

Published target
----------------
Das & Menon, Cerebral Cortex 2024, DOI 10.1093/cercor/bhae287, analyzed the same
UPENN-RAM free-recall family with bipolar iEEG and Phase Transfer Entropy (PTE).
Across participants they reported:

    delta-theta 0.5-8 Hz : HIPP -> parietal > parietal -> HIPP
    beta       12-30 Hz  : parietal -> HIPP > HIPP -> parietal

for both successful encoding and recall.

This script asks only whether one anatomically clean subject/pair shows the same
qualitative frequency-dependent sign flip.  A single subject is NOT a replication
of the group result.

Methods intentionally follow their VFR/PTE description closely:

* bipolar recording;
* 1.6 s after WORD onset for successfully recalled encoding items;
* 1.6 s before REC_WORD vocal onset for recall, excluding overlapping windows;
* 4th-order zero-phase Butterworth band filtering;
* Hilbert instantaneous phase;
* histogram PTE / conditional mutual information;
* Scott-rule phase-bin width;
* Hillebrand-style data-derived prediction delay tau = 2M/M_pm;
* trial-wise PTE averaged across trials;
* time-shuffled-phase surrogates.

The paper's text calls ``3.49 * STD * M**(-1/3)`` the number of bins, but that
expression has the units and form of Scott's *bin width*.  Here we use it as a bin
width on [-pi, pi] and derive the integer bin count.  This implementation choice is
printed and must remain explicit.

Run locally after downloading or let the GitHub workflow fetch the EDF:

    python experiments/fr1_pte_calibration.py --edf /path/to/bipolar.edf \
        --events /path/to/events.tsv

No new biological claim should be made unless this calibration first behaves sanely.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyedflib
from scipy.signal import butter, hilbert, sosfiltfilt


SFREQ_EXPECTED = 1000.0
EPOCH_S = 1.6
HIPP_CH = "LB2-LB3"
PAR_CH = "LH11-LH12"
BANDS = {
    "delta_theta": (0.5, 8.0),
    "beta": (12.0, 30.0),
}


@dataclass(frozen=True)
class EpochSet:
    name: str
    starts: np.ndarray
    stops: np.ndarray


def read_events(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8")), delimiter="\t"))


def successful_encoding_epochs(events: list[dict[str, str]], sfreq: float) -> EpochSet:
    recalled = {
        (row.get("list", ""), row.get("item_name", ""))
        for row in events
        if row.get("trial_type") == "REC_WORD" and row.get("item_name") not in {"", "n/a", "<>"}
    }
    n = int(round(EPOCH_S * sfreq))
    starts = []
    for row in events:
        if row.get("trial_type") != "WORD":
            continue
        key = (row.get("list", ""), row.get("item_name", ""))
        if key not in recalled:
            continue
        starts.append(int(float(row["sample"])))
    starts = np.asarray(sorted(starts), dtype=np.int64)
    return EpochSet("successful_encoding", starts, starts + n)


def recall_epochs(events: list[dict[str, str]], sfreq: float) -> EpochSet:
    n = int(round(EPOCH_S * sfreq))
    vocal = sorted(
        int(float(row["sample"]))
        for row in events
        if row.get("trial_type") == "REC_WORD"
    )
    starts = []
    stops = []
    previous_start = None
    previous_stop = None
    for stop in vocal:
        start = stop - n
        if start < 0:
            continue
        # Das & Menon excluded recall epochs overlapping the prior recall epoch.
        # Since all windows have equal length, adjacent vocal onsets closer than 1.6 s
        # produce overlap. Keep the earlier accepted epoch and drop the later one.
        if previous_start is not None and start < int(previous_stop):
            continue
        starts.append(start)
        stops.append(stop)
        previous_start, previous_stop = start, stop
    return EpochSet(
        "recall",
        np.asarray(starts, dtype=np.int64),
        np.asarray(stops, dtype=np.int64),
    )


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    sd = float(np.std(x))
    if sd <= 0:
        raise ValueError("constant channel")
    return (x - np.mean(x)) / sd


def band_phase(x: np.ndarray, sfreq: float, lo: float, hi: float) -> np.ndarray:
    sos = butter(4, [lo, hi], btype="bandpass", fs=sfreq, output="sos")
    filtered = sosfiltfilt(sos, x)
    return np.angle(hilbert(filtered))


def phase_bin_count(x_phase: np.ndarray, y_phase: np.ndarray) -> tuple[int, float]:
    m = len(x_phase)
    avg_sd = 0.5 * (float(np.std(x_phase)) + float(np.std(y_phase)))
    width = 3.49 * avg_sd * (m ** (-1.0 / 3.0))
    if not np.isfinite(width) or width <= 0:
        return 12, float("nan")
    bins = int(math.ceil((2.0 * math.pi) / width))
    # Tiny trial histograms explode in variance with too many phase bins.
    return int(np.clip(bins, 4, 48)), float(width)


def prediction_delay(x_phase: np.ndarray, y_phase: np.ndarray) -> int:
    """Hillebrand/Das text: tau = 2M / M_pm for two phase channels."""
    m = len(x_phase)
    changes = 0
    for phase in (x_phase, y_phase):
        changes += int(np.count_nonzero(np.diff(np.signbit(phase))))
    if changes <= 0:
        return max(1, m // 20)
    tau = int(round((2.0 * m) / changes))
    return int(np.clip(tau, 1, max(1, m // 3)))


def discretize_phase(phase: np.ndarray, bins: int) -> np.ndarray:
    edges = np.linspace(-math.pi, math.pi, bins + 1)
    idx = np.searchsorted(edges, phase, side="right") - 1
    return np.clip(idx, 0, bins - 1).astype(np.int32)


def phase_transfer_entropy(source: np.ndarray, target: np.ndarray) -> tuple[float, int, int, float]:
    """PTE(source -> target) = I(source_t ; target_{t+tau} | target_t)."""
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    if source.shape != target.shape or source.ndim != 1:
        raise ValueError("source/target phases must be same-length vectors")

    bins, width = phase_bin_count(source, target)
    tau = prediction_delay(source, target)
    if len(source) - tau < 50:
        raise ValueError("too few samples after prediction delay")

    s = discretize_phase(source[:-tau], bins)
    yp = discretize_phase(target[:-tau], bins)
    yf = discretize_phase(target[tau:], bins)
    n = len(s)

    # Counts for p(y_future, y_past, source_past), p(y_past, source_past),
    # p(y_future, y_past), and p(y_past).
    triple = np.zeros((bins, bins, bins), dtype=np.int64)
    yp_s = np.zeros((bins, bins), dtype=np.int64)
    yf_yp = np.zeros((bins, bins), dtype=np.int64)
    yp_count = np.zeros(bins, dtype=np.int64)
    np.add.at(triple, (yf, yp, s), 1)
    np.add.at(yp_s, (yp, s), 1)
    np.add.at(yf_yp, (yf, yp), 1)
    np.add.at(yp_count, yp, 1)

    a, b, c = np.nonzero(triple)
    counts = triple[a, b, c].astype(np.float64)
    p_joint = counts / n
    p_yf_given_yps = counts / yp_s[b, c]
    p_yf_given_yp = yf_yp[a, b] / yp_count[b]
    ratio = p_yf_given_yps / p_yf_given_yp
    te = float(np.sum(p_joint * np.log2(ratio)))
    return te, tau, bins, width


def extract_epoch(phase: np.ndarray, start: int, stop: int) -> np.ndarray | None:
    if start < 0 or stop > len(phase) or stop <= start:
        return None
    x = phase[start:stop]
    if len(x) < 100:
        return None
    return x


def trial_pte(
    source_phase: np.ndarray,
    target_phase: np.ndarray,
    epochs: EpochSet,
) -> tuple[np.ndarray, list[int], list[int]]:
    values = []
    taus = []
    bins = []
    for start, stop in zip(epochs.starts, epochs.stops):
        x = extract_epoch(source_phase, int(start), int(stop))
        y = extract_epoch(target_phase, int(start), int(stop))
        if x is None or y is None:
            continue
        te, tau, nbins, _ = phase_transfer_entropy(x, y)
        values.append(te)
        taus.append(tau)
        bins.append(nbins)
    return np.asarray(values, dtype=np.float64), taus, bins


def surrogate_direction_index(
    hip_phase: np.ndarray,
    par_phase: np.ndarray,
    epochs: EpochSet,
    n_surrogates: int,
    seed: int,
) -> np.ndarray:
    """Paper-style time-shuffled phase null, returning mean directional index."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_surrogates):
        hp = []
        ph = []
        for start, stop in zip(epochs.starts, epochs.stops):
            h = extract_epoch(hip_phase, int(start), int(stop))
            p = extract_epoch(par_phase, int(start), int(stop))
            if h is None or p is None:
                continue
            # Independent time shuffling destroys within/between-series predictability,
            # matching the verbal surrogate description in Das & Menon.
            hs = h[rng.permutation(len(h))]
            ps = p[rng.permutation(len(p))]
            hp.append(phase_transfer_entropy(hs, ps)[0])
            ph.append(phase_transfer_entropy(ps, hs)[0])
        if not hp:
            continue
        mhp = float(np.mean(hp))
        mph = float(np.mean(ph))
        denom = mhp + mph
        out.append((mhp - mph) / denom if denom > 0 else 0.0)
    return np.asarray(out, dtype=np.float64)


def summarize_band(
    hip_phase: np.ndarray,
    par_phase: np.ndarray,
    epochs: EpochSet,
    n_surrogates: int,
    seed: int,
) -> dict[str, object]:
    hp, tau_hp, bins_hp = trial_pte(hip_phase, par_phase, epochs)
    ph, tau_ph, bins_ph = trial_pte(par_phase, hip_phase, epochs)
    n = min(len(hp), len(ph))
    hp, ph = hp[:n], ph[:n]
    if n == 0:
        raise RuntimeError(f"no valid {epochs.name} epochs")
    mean_hp = float(np.mean(hp))
    mean_ph = float(np.mean(ph))
    denom = mean_hp + mean_ph
    di = (mean_hp - mean_ph) / denom if denom > 0 else 0.0
    paired_di = (hp - ph) / np.maximum(hp + ph, 1e-12)

    null = surrogate_direction_index(
        hip_phase, par_phase, epochs, n_surrogates=n_surrogates, seed=seed
    )
    if len(null):
        # Two-sided empirical p around zero directional bias.
        p_two = (1 + np.count_nonzero(np.abs(null) >= abs(di))) / (1 + len(null))
        z = (di - float(np.mean(null))) / max(float(np.std(null)), 1e-12)
    else:
        p_two = float("nan")
        z = float("nan")

    return {
        "epochs": epochs.name,
        "n_trials": int(n),
        "hipp_to_parietal_mean_pte_bits": mean_hp,
        "parietal_to_hipp_mean_pte_bits": mean_ph,
        "direction_index_hipp_positive": float(di),
        "paired_direction_index_mean": float(np.mean(paired_di)),
        "paired_direction_index_sd": float(np.std(paired_di)),
        "tau_samples_median": float(np.median(tau_hp + tau_ph)),
        "tau_ms_median": float(np.median(tau_hp + tau_ph) * 1000.0 / SFREQ_EXPECTED),
        "phase_bins_median": float(np.median(bins_hp + bins_ph)),
        "surrogates": int(len(null)),
        "surrogate_direction_mean": float(np.mean(null)) if len(null) else float("nan"),
        "surrogate_direction_sd": float(np.std(null)) if len(null) else float("nan"),
        "surrogate_two_sided_p": float(p_two),
        "surrogate_z": float(z),
    }


def synthetic_self_test() -> dict[str, float]:
    """Known-direction sanity check for the PTE implementation."""
    rng = np.random.default_rng(123)
    n = 12000
    t = np.arange(n) / 1000.0
    # Source is a frequency-modulated oscillator. Target receives a delayed source
    # plus independent phase modulation; reverse prediction should be weaker.
    source_signal = np.sin(2 * np.pi * 5.0 * t + 0.6 * np.sin(2 * np.pi * 0.7 * t))
    delay = 45
    target_signal = np.zeros_like(source_signal)
    target_signal[delay:] = source_signal[:-delay]
    target_signal += 0.45 * rng.normal(size=n)
    source_signal += 0.15 * rng.normal(size=n)
    sp = np.angle(hilbert(source_signal))
    tp = np.angle(hilbert(target_signal))
    forward = phase_transfer_entropy(sp, tp)[0]
    reverse = phase_transfer_entropy(tp, sp)[0]
    return {"forward": float(forward), "reverse": float(reverse), "difference": float(forward - reverse)}


def load_edf_channels(path: Path, names: tuple[str, str]) -> tuple[float, np.ndarray, np.ndarray]:
    reader = pyedflib.EdfReader(str(path))
    try:
        labels = [x.strip() for x in reader.getSignalLabels()]
        missing = [name for name in names if name not in labels]
        if missing:
            raise KeyError(f"EDF missing channels {missing}; first labels={labels[:20]}")
        idx = [labels.index(name) for name in names]
        sfreqs = [float(reader.getSampleFrequency(i)) for i in idx]
        if max(sfreqs) - min(sfreqs) > 1e-6:
            raise ValueError(f"channel sample rates differ: {sfreqs}")
        signals = [np.asarray(reader.readSignal(i), dtype=np.float64) for i in idx]
        return sfreqs[0], signals[0], signals[1]
    finally:
        reader.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--edf", type=Path)
    p.add_argument("--events", type=Path)
    p.add_argument("--surrogates", type=int, default=100)
    p.add_argument("--out", type=Path, default=Path("results/fr1-pte-r1022j.json"))
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args()

    synthetic = synthetic_self_test()
    print("PTE synthetic self-test:", json.dumps(synthetic, indent=2))
    if synthetic["difference"] <= 0:
        raise RuntimeError("PTE synthetic direction self-test failed")
    if args.synthetic_only:
        return
    if args.edf is None or args.events is None:
        raise SystemExit("--edf and --events are required unless --synthetic-only")

    sfreq, hip_raw, par_raw = load_edf_channels(args.edf, (HIPP_CH, PAR_CH))
    print(f"EDF selected channels: {HIPP_CH}, {PAR_CH}; sfreq={sfreq:g}; samples={len(hip_raw)}")
    if abs(sfreq - SFREQ_EXPECTED) > 1e-6:
        print(f"WARNING expected {SFREQ_EXPECTED:g} Hz from BIDS metadata, got {sfreq:g}")

    hip_raw = zscore(hip_raw)
    par_raw = zscore(par_raw)
    events = read_events(args.events)
    encoding = successful_encoding_epochs(events, sfreq)
    recall = recall_epochs(events, sfreq)
    print(f"candidate epochs: encoding={len(encoding.starts)} recall_nonoverlap={len(recall.starts)}")

    results: dict[str, object] = {
        "subject": "R1022J",
        "session": 0,
        "hippocampus_channel": HIPP_CH,
        "parietal_channel": PAR_CH,
        "sfreq": sfreq,
        "synthetic_self_test": synthetic,
        "binning_note": "Scott expression treated as phase-bin width; integer bins=ceil(2pi/width)",
        "bands": {},
    }

    for band_i, (band_name, (lo, hi)) in enumerate(BANDS.items()):
        print(f"\nBand {band_name} {lo:g}-{hi:g} Hz")
        hip_phase = band_phase(hip_raw, sfreq, lo, hi)
        par_phase = band_phase(par_raw, sfreq, lo, hi)
        band_rows = {}
        for epoch_i, epochs in enumerate((encoding, recall)):
            row = summarize_band(
                hip_phase,
                par_phase,
                epochs,
                n_surrogates=args.surrogates,
                seed=1000 + 100 * band_i + epoch_i,
            )
            band_rows[epochs.name] = row
            print(json.dumps(row, indent=2))
        results["bands"][band_name] = band_rows

    # Qualitative calibration target. One subject/pair is allowed to fail; this only
    # records whether its signs line up with the published group-level pattern.
    dt = results["bands"]["delta_theta"]
    beta = results["bands"]["beta"]
    signs = {
        "delta_theta_encoding_hipp_positive": dt["successful_encoding"]["direction_index_hipp_positive"] > 0,
        "delta_theta_recall_hipp_positive": dt["recall"]["direction_index_hipp_positive"] > 0,
        "beta_encoding_parietal_positive": beta["successful_encoding"]["direction_index_hipp_positive"] < 0,
        "beta_recall_parietal_positive": beta["recall"]["direction_index_hipp_positive"] < 0,
    }
    results["qualitative_group_pattern_signs"] = signs
    results["qualitative_signs_matched"] = int(sum(signs.values()))
    print("\nQualitative published-group sign checks:")
    print(json.dumps(signs, indent=2))
    print(f"matched {sum(signs.values())}/4 signs")
    print("Guardrail: this is one subject and one channel pair, not a replication test.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
