"""Attack the R1022J ACW-difference <-> PTE-direction result as estimator bias.

The exploratory human-iEEG bridge found that

    ACW50(HIPP) - ACW50(ANG)

strongly covaries with raw delta/theta PTE direction index. Before interpreting that as
state-dependent communication, test a harsher possibility:

    finite-sample PTE may prefer one direction when two signals have different intrinsic
    autocorrelation / predictability, even when there is NO directed coupling.

This script uses the exact ACW and PTE estimators from the real-data analysis on 1.6 s,
1000 Hz synthetic trials.

Null arms
---------
independent
    Two independent OU/AR(1) processes with randomly and independently drawn intrinsic
    time constants. There is no cross-signal information path.

common_drive
    The same independently timed local processes plus a symmetric instantaneous common
    drive. This creates correlation/shared input but still no X->Y or Y->X causal path.

matched_timescale
    Independent processes forced to have equal intrinsic time constants. This checks
    whether any apparent directional bias specifically requires a timescale mismatch.

positive_control
    X drives Y through an explicit delayed term. This verifies that the estimator can
    still recover a real directed path under otherwise similar colored dynamics.

Primary diagnostic
------------------
For each arm report Spearman correlation between measured

    ACW_diff = ACW50(X) - ACW50(Y)

and

    PTE_DI = (PTE_X->Y - PTE_Y->X) / (PTE_X->Y + PTE_Y->X).

If a strong same-sign relation appears in independent/common-drive nulls, the human
association is not interpretable as communication gating without a surrogate correction
that preserves each channel's autocorrelation/spectrum.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt
from scipy.stats import spearmanr

from fr1_acw_pte_bridge import ACW_BAND, PTE_BAND, acw50_seconds
from fr1_pte_calibration import phase_transfer_entropy
from scipy.signal import hilbert


SFREQ = 1000.0
EPOCH_S = 1.6
N = int(SFREQ * EPOCH_S)


def ou_process(rng: np.random.Generator, tau_s: float, n: int = N) -> np.ndarray:
    """Stationary unit-variance discrete OU / AR(1)."""
    a = float(np.exp(-1.0 / (SFREQ * tau_s)))
    innovation = float(np.sqrt(max(1e-12, 1.0 - a * a)))
    eps = rng.normal(size=n)
    x = np.empty(n, dtype=np.float64)
    x[0] = eps[0]
    for i in range(1, n):
        x[i] = a * x[i - 1] + innovation * eps[i]
    return x


def preprocess_pair(x: np.ndarray, y: np.ndarray, acw_sos, low_sos):
    xa = sosfiltfilt(acw_sos, x)
    ya = sosfiltfilt(acw_sos, y)
    xl = sosfiltfilt(low_sos, x)
    yl = sosfiltfilt(low_sos, y)
    xp = np.angle(hilbert(xl))
    yp = np.angle(hilbert(yl))
    return xa, ya, xp, yp


def trial_metrics(x, y, acw_sos, low_sos) -> tuple[float, float, float]:
    xa, ya, xp, yp = preprocess_pair(x, y, acw_sos, low_sos)
    ax = acw50_seconds(xa, SFREQ)
    ay = acw50_seconds(ya, SFREQ)
    xy = phase_transfer_entropy(xp, yp)[0]
    yx = phase_transfer_entropy(yp, xp)[0]
    denom = xy + yx
    di = (xy - yx) / denom if denom > 0 else 0.0
    return ax - ay, di, ax + ay


def simulate_arm(
    arm: str,
    *,
    trials: int,
    seed: int,
    tau_lo: float,
    tau_hi: float,
    common_gain: float,
    drive_gain: float,
    drive_delay_ms: float,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    acw_sos = butter(4, ACW_BAND, btype="bandpass", fs=SFREQ, output="sos")
    low_sos = butter(4, PTE_BAND, btype="bandpass", fs=SFREQ, output="sos")

    acw_diff = []
    pte_di = []
    acw_sum = []
    latent_tau_diff = []

    for _ in range(trials):
        tx = float(np.exp(rng.uniform(np.log(tau_lo), np.log(tau_hi))))
        if arm == "matched_timescale":
            ty = tx
        else:
            ty = float(np.exp(rng.uniform(np.log(tau_lo), np.log(tau_hi))))

        x_local = ou_process(rng, tx)
        y_local = ou_process(rng, ty)

        if arm == "independent" or arm == "matched_timescale":
            x, y = x_local, y_local
        elif arm == "common_drive":
            tc = float(np.exp(rng.uniform(np.log(tau_lo), np.log(tau_hi))))
            common = ou_process(rng, tc)
            x = x_local + common_gain * common
            y = y_local + common_gain * common
        elif arm == "positive_control":
            delay = int(round(drive_delay_ms * SFREQ / 1000.0))
            x = x_local
            y = y_local.copy()
            if 0 < delay < N:
                y[delay:] += drive_gain * x_local[:-delay]
        else:
            raise ValueError(arm)

        d, di, s = trial_metrics(x, y, acw_sos, low_sos)
        acw_diff.append(d)
        pte_di.append(di)
        acw_sum.append(s)
        latent_tau_diff.append(tx - ty)

    acw_diff = np.asarray(acw_diff)
    pte_di = np.asarray(pte_di)
    acw_sum = np.asarray(acw_sum)
    latent_tau_diff = np.asarray(latent_tau_diff)

    rho, p = spearmanr(acw_diff, pte_di)
    rho_sum, p_sum = spearmanr(acw_sum, pte_di)
    rho_latent, p_latent = spearmanr(latent_tau_diff, pte_di)
    return {
        "arm": arm,
        "trials": trials,
        "acw_diff_mean_s": float(np.mean(acw_diff)),
        "acw_diff_sd_s": float(np.std(acw_diff)),
        "pte_di_mean": float(np.mean(pte_di)),
        "pte_di_sd": float(np.std(pte_di)),
        "rho_acw_diff_vs_pte_di": float(rho),
        "p_acw_diff_vs_pte_di": float(p),
        "rho_acw_sum_vs_pte_di": float(rho_sum),
        "p_acw_sum_vs_pte_di": float(p_sum),
        "rho_latent_tau_diff_vs_pte_di": float(rho_latent),
        "p_latent_tau_diff_vs_pte_di": float(p_latent),
        "positive_di_fraction": float(np.mean(pte_di > 0)),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--trials", type=int, default=500)
    p.add_argument("--tau-lo-ms", type=float, default=15.0)
    p.add_argument("--tau-hi-ms", type=float, default=180.0)
    p.add_argument("--common-gain", type=float, default=0.8)
    p.add_argument("--drive-gain", type=float, default=1.2)
    p.add_argument("--drive-delay-ms", type=float, default=45.0)
    p.add_argument("--out", type=Path, default=Path("results/acw-pte-estimator-bias.json"))
    args = p.parse_args()

    arms = ("independent", "matched_timescale", "common_drive", "positive_control")
    rows = []
    for i, arm in enumerate(arms):
        row = simulate_arm(
            arm,
            trials=args.trials,
            seed=4100 + i,
            tau_lo=args.tau_lo_ms / 1000.0,
            tau_hi=args.tau_hi_ms / 1000.0,
            common_gain=args.common_gain,
            drive_gain=args.drive_gain,
            drive_delay_ms=args.drive_delay_ms,
        )
        rows.append(row)
        print(f"\n{arm}")
        print(json.dumps(row, indent=2))

    by_arm = {r["arm"]: r for r in rows}
    print("\nINTERPRETATION GATE")
    null_max = max(
        abs(by_arm["independent"]["rho_acw_diff_vs_pte_di"]),
        abs(by_arm["common_drive"]["rho_acw_diff_vs_pte_di"]),
    )
    print(f"largest |rho| among heterogeneous-timescale nulls = {null_max:.4f}")
    print("R1022J observed raw/partial correlations were approximately:")
    print("  encoding ACWdiff->PTE-DI raw +0.544, power-controlled +0.383")
    print("  recall   ACWdiff->PTE-DI raw +0.689, power-controlled +0.644")
    if null_max >= 0.25:
        print("WARNING: estimator/timescale geometry can manufacture a substantial relation.")
        print("Do not interpret the human ACW-PTE association as communication gating without")
        print("a spectrum/autocorrelation-preserving surrogate correction.")
    else:
        print("The simple nulls did not reproduce a large ACWdiff->PTE-DI relation.")
        print("This does NOT validate the human bridge; next require circular-shift/spectral")
        print("surrogates and independent participants.")

    payload = {"config": vars(args), "rows": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
