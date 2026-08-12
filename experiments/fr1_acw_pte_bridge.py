"""Exploratory bridge: intrinsic neural timescale <-> directed information access.

This does NOT test whether ACW or PTE exists; both are established analysis objects.
It asks whether two 2026-era memory observations couple within one real human iEEG pair:

1. Shen et al. (NeuroImage 2026, DOI 10.1016/j.neuroimage.2025.121634)
   report longer autocorrelation windows (ACW) during encoding than retrieval and define
   ACW as the first ACF lag falling below 50% of its maximum.

2. Das & Menon (Cerebral Cortex 2024, DOI 10.1093/cercor/bhae287)
   report frequency-specific directed hippocampus<->parietal Phase Transfer Entropy.

Question
--------
In the anatomically clean R1022J pair already calibrated in this repo

    HIPP   LB2-LB3   (DG <-> CA1)
    ANG    LH11-LH12 (angular gyrus <-> angular gyrus)

is trial-to-trial temporal integration state associated with delta/theta directed access?

The key exploratory variable is

    DI = (PTE_HIPP->ANG - PTE_ANG->HIPP) / sum(PTE)

versus

    HIPP ACW50
    ANG  ACW50
    mean ACW50
    HIPP-minus-ANG ACW50

Because both ACW and PTE can be influenced by spectral slowing, the script also reports
partial Spearman correlations after controlling for log delta/theta power in both
channels.

Important guardrails
--------------------
* One participant/pair = discovery probe only.
* ACW and PTE are computed from the SAME 1.6 s epoch, so association cannot establish
  temporal precedence.  A positive result would justify a later state-before-flow test.
* The memory tasks differ from Shen's recognition paradigm; encoding>recall ACW is only
  a qualitative calibration, not a replication.
* No sign of the ACW<->PTE relation is preregistered here.  Report it two-sided.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt
from scipy.stats import mannwhitneyu, pearsonr, rankdata, spearmanr

from fr1_pte_calibration import (
    HIPP_CH,
    PAR_CH,
    band_phase,
    load_edf_channels,
    phase_transfer_entropy,
    read_events,
    recall_epochs,
    successful_encoding_epochs,
    zscore,
)


ACW_BAND = (0.5, 40.0)
PTE_BAND = (0.5, 8.0)


def acw50_seconds(x: np.ndarray, sfreq: float) -> float:
    """First positive lag where normalized autocorrelation falls below 0.5."""
    x = np.asarray(x, dtype=np.float64)
    x = x - np.mean(x)
    denom = float(np.dot(x, x))
    if denom <= 1e-15:
        return float("nan")
    # Epochs are only ~1.6 s, so direct correlation is cheap and transparent.
    acf = np.correlate(x, x, mode="full")[len(x) - 1 :] / denom
    below = np.flatnonzero(acf < 0.5)
    if len(below) == 0:
        return (len(x) - 1) / sfreq
    lag = int(below[0])
    if lag == 0:
        return 0.0
    # Linear interpolation across the 0.5 crossing reduces sample-grid quantization.
    y0, y1 = float(acf[lag - 1]), float(acf[lag])
    frac = 0.0 if abs(y1 - y0) < 1e-12 else (0.5 - y0) / (y1 - y0)
    return (lag - 1 + float(np.clip(frac, 0.0, 1.0))) / sfreq


def partial_spearman(x: np.ndarray, y: np.ndarray, covariates: np.ndarray) -> tuple[float, float]:
    """Rank variables, regress ranked covariates, correlate residuals."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    c = np.asarray(covariates, dtype=np.float64)
    mask = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(c), axis=1)
    x, y, c = x[mask], y[mask], c[mask]
    if len(x) < c.shape[1] + 5:
        return float("nan"), float("nan")
    xr = rankdata(x)
    yr = rankdata(y)
    cr = np.column_stack([rankdata(c[:, j]) for j in range(c.shape[1])])
    design = np.column_stack([np.ones(len(x)), cr])
    bx = np.linalg.lstsq(design, xr, rcond=None)[0]
    by = np.linalg.lstsq(design, yr, rcond=None)[0]
    rx = xr - design @ bx
    ry = yr - design @ by
    r, p = pearsonr(rx, ry)
    return float(r), float(p)


def extract_trial_metrics(
    hip_acw_signal: np.ndarray,
    ang_acw_signal: np.ndarray,
    hip_pte_phase: np.ndarray,
    ang_pte_phase: np.ndarray,
    hip_low_signal: np.ndarray,
    ang_low_signal: np.ndarray,
    starts: np.ndarray,
    stops: np.ndarray,
    sfreq: float,
) -> dict[str, np.ndarray]:
    rows = {
        "hip_acw_s": [],
        "ang_acw_s": [],
        "mean_acw_s": [],
        "acw_diff_s": [],
        "pte_di": [],
        "pte_hip_to_ang": [],
        "pte_ang_to_hip": [],
        "hip_log_low_power": [],
        "ang_log_low_power": [],
    }
    n_samples = len(hip_acw_signal)
    for start, stop in zip(starts, stops):
        a, b = int(start), int(stop)
        if a < 0 or b > n_samples or b - a < 100:
            continue
        h = hip_acw_signal[a:b]
        g = ang_acw_signal[a:b]
        hacw = acw50_seconds(h, sfreq)
        gacw = acw50_seconds(g, sfreq)

        hpte = hip_pte_phase[a:b]
        gpte = ang_pte_phase[a:b]
        p_hg = phase_transfer_entropy(hpte, gpte)[0]
        p_gh = phase_transfer_entropy(gpte, hpte)[0]
        denom = p_hg + p_gh
        di = (p_hg - p_gh) / denom if denom > 0 else 0.0

        hp = float(np.mean(hip_low_signal[a:b] ** 2))
        gp = float(np.mean(ang_low_signal[a:b] ** 2))

        rows["hip_acw_s"].append(hacw)
        rows["ang_acw_s"].append(gacw)
        rows["mean_acw_s"].append(0.5 * (hacw + gacw))
        rows["acw_diff_s"].append(hacw - gacw)
        rows["pte_di"].append(di)
        rows["pte_hip_to_ang"].append(p_hg)
        rows["pte_ang_to_hip"].append(p_gh)
        rows["hip_log_low_power"].append(np.log(max(hp, 1e-15)))
        rows["ang_log_low_power"].append(np.log(max(gp, 1e-15)))

    return {k: np.asarray(v, dtype=np.float64) for k, v in rows.items()}


def correlation_table(metrics: dict[str, np.ndarray]) -> dict[str, dict[str, float]]:
    y = metrics["pte_di"]
    cov = np.column_stack(
        [metrics["hip_log_low_power"], metrics["ang_log_low_power"]]
    )
    out = {}
    for name in ("hip_acw_s", "ang_acw_s", "mean_acw_s", "acw_diff_s"):
        rho, p = spearmanr(metrics[name], y, nan_policy="omit")
        pr, pp = partial_spearman(metrics[name], y, cov)
        out[name] = {
            "spearman_rho": float(rho),
            "spearman_p": float(p),
            "partial_spearman_power_control_r": pr,
            "partial_spearman_power_control_p": pp,
        }
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--edf", type=Path, required=True)
    p.add_argument("--events", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("results/fr1-acw-pte-r1022j.json"))
    args = p.parse_args()

    sfreq, hip_raw, ang_raw = load_edf_channels(args.edf, (HIPP_CH, PAR_CH))
    hip_raw = zscore(hip_raw)
    ang_raw = zscore(ang_raw)
    events = read_events(args.events)
    encoding = successful_encoding_epochs(events, sfreq)
    recall = recall_epochs(events, sfreq)

    # Shen: 0.5-40 Hz preprocessing before ACW.  Use a 4th-order zero-phase Butterworth
    # here rather than pretending this is an exact replication of their FIR pipeline.
    acw_sos = butter(4, ACW_BAND, btype="bandpass", fs=sfreq, output="sos")
    hip_acw_signal = sosfiltfilt(acw_sos, hip_raw)
    ang_acw_signal = sosfiltfilt(acw_sos, ang_raw)

    low_sos = butter(4, PTE_BAND, btype="bandpass", fs=sfreq, output="sos")
    hip_low = sosfiltfilt(low_sos, hip_raw)
    ang_low = sosfiltfilt(low_sos, ang_raw)
    hip_phase = band_phase(hip_raw, sfreq, *PTE_BAND)
    ang_phase = band_phase(ang_raw, sfreq, *PTE_BAND)

    enc = extract_trial_metrics(
        hip_acw_signal, ang_acw_signal, hip_phase, ang_phase,
        hip_low, ang_low, encoding.starts, encoding.stops, sfreq,
    )
    rec = extract_trial_metrics(
        hip_acw_signal, ang_acw_signal, hip_phase, ang_phase,
        hip_low, ang_low, recall.starts, recall.stops, sfreq,
    )

    result = {
        "subject": "R1022J",
        "hippocampus_channel": HIPP_CH,
        "angular_channel": PAR_CH,
        "sfreq": sfreq,
        "acw_definition": "first normalized ACF lag below 0.5 after 0.5-40Hz zero-phase filter",
        "pte_band_hz": list(PTE_BAND),
        "n_encoding": int(len(enc["pte_di"])),
        "n_recall": int(len(rec["pte_di"])),
        "state_summary": {},
        "acw_to_pte": {
            "successful_encoding": correlation_table(enc),
            "recall": correlation_table(rec),
        },
    }

    print("R1022J ACW <-> PTE exploratory bridge")
    print(f"encoding n={len(enc['pte_di'])} recall n={len(rec['pte_di'])}")

    for name in ("hip_acw_s", "ang_acw_s", "mean_acw_s"):
        u = mannwhitneyu(enc[name], rec[name], alternative="two-sided")
        row = {
            "encoding_mean_s": float(np.mean(enc[name])),
            "encoding_median_s": float(np.median(enc[name])),
            "recall_mean_s": float(np.mean(rec[name])),
            "recall_median_s": float(np.median(rec[name])),
            "encoding_minus_recall_mean_s": float(np.mean(enc[name]) - np.mean(rec[name])),
            "mannwhitney_u": float(u.statistic),
            "mannwhitney_two_sided_p": float(u.pvalue),
        }
        result["state_summary"][name] = row
        print(f"\n{name}")
        print(json.dumps(row, indent=2))

    for epoch_name, table in result["acw_to_pte"].items():
        print(f"\nACW -> delta/theta PTE-DI association: {epoch_name}")
        print(json.dumps(table, indent=2))

    print("\nGuardrails")
    print("----------")
    print("Encoding-vs-recall ACW is a qualitative cross-task calibration, not Shen replication.")
    print("ACW and PTE-DI are measured in the same epoch; correlation is not temporal gating.")
    print("Power-controlled partial rank correlations are included to reduce the trivial")
    print("possibility that spectral slowing alone creates both quantities.")
    print("Any association here must replicate across independently selected participants")
    print("and then be retested with state measured BEFORE the directed-flow window.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
