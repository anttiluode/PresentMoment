"""Trial-level inference for the first real FR1 PTE calibration.

The original one-subject calibration used paper-style time-shuffled phase surrogates.
Those are useful for asking whether the observed phase relationship differs from a
randomized phase null, but the aggregate surrogate mean can become extremely narrow after
averaging many trials.  That made even the tiny beta directional index look numerically
more decisive than is sensible for one subject/pair.

This companion script therefore asks a harsher and simpler question:

    Across trials, is PTE(HIPP->PAR) systematically larger/smaller than
    PTE(PAR->HIPP)?

For each band and epoch family it reports:

* paired raw PTE difference per trial;
* paired direction index per trial;
* exact Monte-Carlo sign-flip permutation p-value for the mean paired difference;
* bootstrap 95% CI for the mean direction index;
* Wilcoxon signed-rank p-value as a rank-based descriptive cross-check;
* sign consistency (fraction of trials in the published group-level direction).

This is still one subject and one channel pair. Trials from the same recording are not
independent subjects, so these p-values do NOT substitute for a participant-level
replication.

Run:
    python experiments/fr1_pte_trial_stats.py --edf data/R1022J_bipolar.edf \
        --events data/R1022J_events.tsv
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

from fr1_pte_calibration import (
    BANDS,
    HIPP_CH,
    PAR_CH,
    band_phase,
    load_edf_channels,
    read_events,
    recall_epochs,
    successful_encoding_epochs,
    trial_pte,
    zscore,
)


def sign_flip_p(values: np.ndarray, *, draws: int, seed: int) -> float:
    """Two-sided random sign-flip test of a paired mean against zero."""
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return float("nan")
    observed = abs(float(np.mean(values)))
    rng = np.random.default_rng(seed)
    extreme = 0
    # Chunk to avoid a large draws x trials allocation.
    left = int(draws)
    while left > 0:
        n = min(left, 4096)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(n, len(values)))
        means = np.mean(signs * values[None, :], axis=1)
        extreme += int(np.count_nonzero(np.abs(means) >= observed))
        left -= n
    return float((extreme + 1) / (draws + 1))


def bootstrap_ci(values: np.ndarray, *, draws: int, seed: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = np.empty(draws, dtype=np.float64)
    for i in range(draws):
        idx = rng.integers(0, len(values), size=len(values))
        means[i] = float(np.mean(values[idx]))
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(lo), float(hi)


def summarize_trials(
    hip_phase: np.ndarray,
    par_phase: np.ndarray,
    epochs,
    *,
    expected_sign: int,
    seed: int,
    permutation_draws: int,
    bootstrap_draws: int,
) -> dict[str, object]:
    hp, _, _ = trial_pte(hip_phase, par_phase, epochs)
    ph, _, _ = trial_pte(par_phase, hip_phase, epochs)
    n = min(len(hp), len(ph))
    hp = hp[:n]
    ph = ph[:n]
    diff = hp - ph
    trial_di = diff / np.maximum(hp + ph, 1e-12)

    flip_p = sign_flip_p(diff, draws=permutation_draws, seed=seed)
    ci_lo, ci_hi = bootstrap_ci(trial_di, draws=bootstrap_draws, seed=seed + 1)
    try:
        w = wilcoxon(diff, alternative="two-sided", zero_method="wilcox")
        wilcoxon_stat = float(w.statistic)
        wilcoxon_p = float(w.pvalue)
    except ValueError:
        wilcoxon_stat = float("nan")
        wilcoxon_p = float("nan")

    directional_fraction = float(np.mean(expected_sign * diff > 0))
    mean_diff = float(np.mean(diff))
    sd_diff = float(np.std(diff, ddof=1)) if n > 1 else 0.0
    dz = mean_diff / sd_diff if sd_diff > 0 else float("nan")

    return {
        "epochs": epochs.name,
        "n_trials": int(n),
        "expected_sign": int(expected_sign),
        "hipp_to_parietal_mean_pte_bits": float(np.mean(hp)),
        "parietal_to_hipp_mean_pte_bits": float(np.mean(ph)),
        "paired_pte_difference_mean_bits": mean_diff,
        "paired_pte_difference_sd_bits": sd_diff,
        "paired_effect_dz": float(dz),
        "paired_direction_index_mean": float(np.mean(trial_di)),
        "paired_direction_index_ci95": [ci_lo, ci_hi],
        "paired_sign_flip_p": flip_p,
        "wilcoxon_statistic": wilcoxon_stat,
        "wilcoxon_two_sided_p": wilcoxon_p,
        "fraction_trials_in_published_direction": directional_fraction,
        "positive_trial_fraction": float(np.mean(diff > 0)),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--edf", type=Path, required=True)
    p.add_argument("--events", type=Path, required=True)
    p.add_argument("--permutations", type=int, default=50000)
    p.add_argument("--bootstraps", type=int, default=20000)
    p.add_argument("--out", type=Path, default=Path("results/fr1-pte-r1022j-trial-stats.json"))
    args = p.parse_args()

    sfreq, hip_raw, par_raw = load_edf_channels(args.edf, (HIPP_CH, PAR_CH))
    hip_raw = zscore(hip_raw)
    par_raw = zscore(par_raw)
    events = read_events(args.events)
    epoch_sets = (successful_encoding_epochs(events, sfreq), recall_epochs(events, sfreq))

    result: dict[str, object] = {
        "subject": "R1022J",
        "hippocampus_channel": HIPP_CH,
        "parietal_channel": PAR_CH,
        "sfreq": sfreq,
        "permutation_draws": args.permutations,
        "bootstrap_draws": args.bootstraps,
        "bands": {},
    }

    for band_i, (band_name, (lo, hi)) in enumerate(BANDS.items()):
        hip_phase = band_phase(hip_raw, sfreq, lo, hi)
        par_phase = band_phase(par_raw, sfreq, lo, hi)
        expected_sign = +1 if band_name == "delta_theta" else -1
        rows = {}
        print(f"\n{band_name} {lo:g}-{hi:g} Hz expected_sign={expected_sign:+d}")
        for epoch_i, epochs in enumerate(epoch_sets):
            row = summarize_trials(
                hip_phase,
                par_phase,
                epochs,
                expected_sign=expected_sign,
                seed=7000 + band_i * 100 + epoch_i,
                permutation_draws=args.permutations,
                bootstrap_draws=args.bootstraps,
            )
            rows[epochs.name] = row
            print(json.dumps(row, indent=2))
        result["bands"][band_name] = rows

    print("\nInterpretation guardrail")
    print("------------------------")
    print("These are within-recording trial statistics, not independent-subject inference.")
    print("A sign that survives here is worth taking to more participants; it is not a")
    print("population replication by itself.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
