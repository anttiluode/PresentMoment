"""Real-data null for the R1022J ACW-difference <-> PTE-direction bridge.

Observed exploratory result
---------------------------
In the anatomically clean R1022J hippocampus-angular pair, trial-wise

    ACW50(HIPP) - ACW50(ANG)

strongly covaried with raw delta/theta PTE direction index during both successful
encoding and recall.

That association can still be non-communicative.  PTE finite-sample bias or generic
signal statistics may create direction as a function of sender/receiver timescale.

This control preserves REAL waveforms and marginal temporal structure while destroying
the matched interregional trial relation.

For each task epoch family:

1. precompute each hippocampal trial waveform/phase/ACW/power;
2. precompute each angular trial waveform/phase/ACW/power;
3. compute the observed same-trial ACWdiff->PTE-DI correlation;
4. repeatedly derange angular trial labels so HIPP trial i is paired with ANG trial j!=i;
5. recompute PTE direction, ACW difference and power-controlled partial rank correlation.

Because the shuffled pairs preserve each channel's actual ACW/spectrum distributions and
task alignment but destroy trial-specific interregional pairing, the resulting null asks:

    Is the observed ACWdiff->PTE direction relation stronger than what the two marginal
    channel dynamics + estimator produce on their own?

This is still not a causal test.  Passing this null only earns a more stringent
state-before-flow experiment.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, hilbert, sosfiltfilt
from scipy.stats import spearmanr

from fr1_acw_pte_bridge import (
    ACW_BAND,
    PTE_BAND,
    acw50_seconds,
    partial_spearman,
)
from fr1_pte_calibration import (
    HIPP_CH,
    PAR_CH,
    load_edf_channels,
    phase_transfer_entropy,
    read_events,
    recall_epochs,
    successful_encoding_epochs,
    zscore,
)


class Trial:
    __slots__ = ("acw", "phase", "log_power")

    def __init__(self, acw: float, phase: np.ndarray, log_power: float):
        self.acw = float(acw)
        self.phase = np.asarray(phase, dtype=np.float64)
        self.log_power = float(log_power)


def make_trials(
    raw: np.ndarray,
    starts: np.ndarray,
    stops: np.ndarray,
    sfreq: float,
) -> list[Trial]:
    acw_sos = butter(4, ACW_BAND, btype="bandpass", fs=sfreq, output="sos")
    low_sos = butter(4, PTE_BAND, btype="bandpass", fs=sfreq, output="sos")
    acw_signal = sosfiltfilt(acw_sos, raw)
    low_signal = sosfiltfilt(low_sos, raw)
    phase = np.angle(hilbert(low_signal))

    out = []
    for start, stop in zip(starts, stops):
        a, b = int(start), int(stop)
        if a < 0 or b > len(raw) or b - a < 100:
            continue
        x_acw = acw_signal[a:b]
        x_low = low_signal[a:b]
        out.append(
            Trial(
                acw50_seconds(x_acw, sfreq),
                phase[a:b],
                np.log(max(float(np.mean(x_low * x_low)), 1e-15)),
            )
        )
    return out


def derangement(rng: np.random.Generator, n: int) -> np.ndarray:
    """Random permutation with no fixed points."""
    if n < 2:
        raise ValueError("need at least two trials")
    while True:
        p = rng.permutation(n)
        if np.all(p != np.arange(n)):
            return p


def paired_metrics(hip: list[Trial], ang: list[Trial], pairing: np.ndarray) -> dict[str, float]:
    n = min(len(hip), len(ang), len(pairing))
    acw_diff = np.empty(n, dtype=np.float64)
    pte_di = np.empty(n, dtype=np.float64)
    powers = np.empty((n, 2), dtype=np.float64)

    for i in range(n):
        h = hip[i]
        a = ang[int(pairing[i])]
        h_to_a = phase_transfer_entropy(h.phase, a.phase)[0]
        a_to_h = phase_transfer_entropy(a.phase, h.phase)[0]
        denom = h_to_a + a_to_h
        acw_diff[i] = h.acw - a.acw
        pte_di[i] = (h_to_a - a_to_h) / denom if denom > 0 else 0.0
        powers[i] = [h.log_power, a.log_power]

    rho, p = spearmanr(acw_diff, pte_di)
    partial_r, partial_p = partial_spearman(acw_diff, pte_di, powers)
    return {
        "rho": float(rho),
        "p": float(p),
        "partial_r_power": float(partial_r),
        "partial_p_power": float(partial_p),
        "pte_di_mean": float(np.mean(pte_di)),
        "acw_diff_mean": float(np.mean(acw_diff)),
    }


def run_epoch(
    name: str,
    hip: list[Trial],
    ang: list[Trial],
    *,
    permutations: int,
    seed: int,
) -> dict[str, object]:
    n = min(len(hip), len(ang))
    hip = hip[:n]
    ang = ang[:n]
    observed = paired_metrics(hip, ang, np.arange(n))

    rng = np.random.default_rng(seed)
    null_rho = np.empty(permutations, dtype=np.float64)
    null_partial = np.empty(permutations, dtype=np.float64)
    for k in range(permutations):
        pair = derangement(rng, n)
        row = paired_metrics(hip, ang, pair)
        null_rho[k] = row["rho"]
        null_partial[k] = row["partial_r_power"]

    def empirical(obs: float, null: np.ndarray) -> dict[str, float]:
        two = (1 + np.count_nonzero(np.abs(null) >= abs(obs))) / (1 + len(null))
        upper = (1 + np.count_nonzero(null >= obs)) / (1 + len(null))
        z = (obs - float(np.mean(null))) / max(float(np.std(null)), 1e-12)
        return {
            "null_mean": float(np.mean(null)),
            "null_sd": float(np.std(null)),
            "null_q025": float(np.quantile(null, 0.025)),
            "null_q975": float(np.quantile(null, 0.975)),
            "empirical_two_sided_p": float(two),
            "empirical_upper_p": float(upper),
            "z_vs_null": float(z),
        }

    return {
        "epochs": name,
        "n_trials": n,
        "observed": observed,
        "pairing_null_raw_rho": empirical(observed["rho"], null_rho),
        "pairing_null_power_partial_r": empirical(observed["partial_r_power"], null_partial),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--edf", type=Path, required=True)
    p.add_argument("--events", type=Path, required=True)
    p.add_argument("--permutations", type=int, default=200)
    p.add_argument("--out", type=Path, default=Path("results/fr1-acw-pte-pairing-null.json"))
    args = p.parse_args()

    sfreq, hip_raw, ang_raw = load_edf_channels(args.edf, (HIPP_CH, PAR_CH))
    hip_raw = zscore(hip_raw)
    ang_raw = zscore(ang_raw)
    events = read_events(args.events)
    epoch_sets = (
        successful_encoding_epochs(events, sfreq),
        recall_epochs(events, sfreq),
    )

    result = {
        "subject": "R1022J",
        "hippocampus_channel": HIPP_CH,
        "angular_channel": PAR_CH,
        "permutations": args.permutations,
        "epochs": {},
    }

    for idx, epoch_set in enumerate(epoch_sets):
        hip = make_trials(hip_raw, epoch_set.starts, epoch_set.stops, sfreq)
        ang = make_trials(ang_raw, epoch_set.starts, epoch_set.stops, sfreq)
        row = run_epoch(
            epoch_set.name,
            hip,
            ang,
            permutations=args.permutations,
            seed=8800 + idx,
        )
        result["epochs"][epoch_set.name] = row
        print(f"\n{epoch_set.name}")
        print(json.dumps(row, indent=2))

    print("\nInterpretation")
    print("--------------")
    print("If observed ACWdiff->PTE-DI correlation sits inside the mismatched-trial null,")
    print("the bridge is explained by marginal signal/estimator geometry and should be killed.")
    print("If it exceeds the null, trial-specific interregional organization contributes beyond")
    print("those marginals; still require replication and a state-before-flow temporal test.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
