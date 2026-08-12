"""Deadline sweep: asynchronous partial maturity vs synchronized layer barriers.

This is a *scheduling / state-availability* toy, not a claim that the brain or KYY
has been modelled faithfully.

Question
--------
Suppose several local branches refine evidence through the same number of stages,
but their physical step delays differ.

ASYNC:
    each branch advances as soon as its own previous step finishes.
    At any read time, branches can coexist at different maturities.

SYNC:
    after each stage, every branch waits for the slowest branch before the next
    stage begins.  We give this baseline an *early-exit readout after every
    completed barrier*, so it does not need a learned halting controller.

Both schedules use:
    * exactly the same branch evidence,
    * exactly the same per-stage estimates,
    * exactly the same local step delays,
    * exactly the same final linear readout.

Only the synchronization rule differs.

The task is binary classification from multiple noisy evidence branches. Later
refinement stages reduce branch-estimate noise. We sweep a hard external deadline
and ask what can be read *right now*.

A second "fast-conflict" regime deliberately makes some of the fastest branches
misleading on a subset of episodes. This is not a biological model; it checks the
other side of partial maturity: early availability can produce premature errors
that are later corrected.

Interpretation guardrail
------------------------
This demo is almost guaranteed to favor asynchronous scheduling before the final
barrier because that is the property being isolated. It is therefore a mechanism
sanity check, not an architectural win over Transformers, early-exit networks,
SNNs, or any trained baseline.

The next real experiment should replace these synthetic refinement stages with a
trainable local-delay model and compare against strong anytime / asynchronous
baselines under matched compute and training.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import numpy as np


@dataclass(frozen=True)
class Config:
    branches: int = 12
    depth: int = 5
    episodes: int = 10_000
    seeds: int = 10
    base_step_time: float = 0.18
    delay_log_sd: float = 0.55
    evidence_noise_sd: float = 1.10
    conflict_fraction: float = 0.35
    conflict_fast_shift: float = 1.20
    conflict_slow_shift: float = 0.50

    # stage 0 has no label information; stages 1..depth are progressively cleaner
    stage_noise_sd: tuple[float, ...] = (0.0, 2.0, 1.3, 0.8, 0.45, 0.18)

    # deadlines as fractions of the synchronized schedule's complete latency
    deadlines: tuple[float, ...] = tuple(np.linspace(0.0, 1.0, 21))


def make_delays(rng: np.random.Generator, cfg: Config) -> np.ndarray:
    """One fixed heterogeneous local-delay fabric for a seed."""
    delays = np.exp(
        rng.normal(
            np.log(cfg.base_step_time),
            cfg.delay_log_sd,
            size=(cfg.branches, cfg.depth),
        )
    )
    # Only for reproducible interpretation of the conflict regime:
    # branch index then goes approximately fastest -> slowest by total path time.
    order = np.argsort(delays.sum(axis=1))
    return delays[order]


def make_episode_estimates(
    rng: np.random.Generator,
    cfg: Config,
    *,
    fast_conflict: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """Return labels y and branch estimates at maturities k=0..depth."""
    y = rng.choice(np.array([-1.0, 1.0]), size=cfg.episodes)

    # Slower branches are modestly stronger on average. This is not required for
    # the neutral scheduling effect but creates a useful premature-response stress
    # condition when fast_conflict=True.
    strengths = np.linspace(0.25, 0.95, cfg.branches)
    latent = (
        y[:, None] * strengths[None, :]
        + rng.normal(0.0, cfg.evidence_noise_sd, size=(cfg.episodes, cfg.branches))
    )

    if fast_conflict:
        conflict = rng.random(cfg.episodes) < cfg.conflict_fraction
        q = cfg.branches // 3

        # On conflict episodes, fast channels are shifted against the label while
        # slow channels get a smaller correcting shift.
        latent[conflict, :q] -= (
            y[conflict, None] * cfg.conflict_fast_shift
        )
        latent[conflict, -q:] += (
            y[conflict, None] * cfg.conflict_slow_shift
        )

    estimates = np.zeros((cfg.episodes, cfg.branches, cfg.depth + 1))

    # Before any computation finishes, the readout sees non-informative state.
    estimates[:, :, 0] = rng.normal(
        0.0, 1.0, size=(cfg.episodes, cfg.branches)
    )

    stage_noise = np.asarray(cfg.stage_noise_sd, dtype=float)
    if len(stage_noise) != cfg.depth + 1:
        raise ValueError("stage_noise_sd must have depth+1 entries")

    for k in range(1, cfg.depth + 1):
        estimates[:, :, k] = latent + rng.normal(
            0.0,
            stage_noise[k],
            size=(cfg.episodes, cfg.branches),
        )

    return y, estimates


def schedule_times(delays: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Completion times for async branches and synchronized layer barriers."""
    async_complete = np.cumsum(delays, axis=1)  # [branch, stage]

    # Synchronization: stage k+1 starts only after every branch completes stage k.
    sync_stage_duration = delays.max(axis=0)
    sync_complete = np.cumsum(sync_stage_duration)  # [stage]
    full_sync_time = float(sync_complete[-1])
    return async_complete, sync_complete, full_sync_time


def maturity_async(async_complete: np.ndarray, deadline: float) -> np.ndarray:
    """Per-branch number of completed refinement stages."""
    return (async_complete <= deadline).sum(axis=1).astype(int)


def maturity_sync(sync_complete: np.ndarray, deadline: float, branches: int) -> np.ndarray:
    """All branches have the same maturity under layer synchronization."""
    k = int((sync_complete <= deadline).sum())
    return np.full(branches, k, dtype=int)


def predict(
    estimates: np.ndarray,
    maturity: np.ndarray,
) -> np.ndarray:
    """Same fixed sum readout for both schedules."""
    # estimates [episode, branch, stage], maturity [branch]
    chosen = np.take_along_axis(
        estimates,
        np.broadcast_to(
            maturity[None, :, None],
            (estimates.shape[0], estimates.shape[1], 1),
        ),
        axis=2,
    )[:, :, 0]
    logit = chosen.sum(axis=1)
    return np.where(logit >= 0.0, 1.0, -1.0)


def run_seed(seed: int, cfg: Config, *, fast_conflict: bool) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    delays = make_delays(rng, cfg)
    y, estimates = make_episode_estimates(
        rng, cfg, fast_conflict=fast_conflict
    )
    async_complete, sync_complete, full_sync = schedule_times(delays)

    acc_async = []
    acc_sync = []
    depth_async = []
    depth_sync = []
    preds_async = []

    for fraction in cfg.deadlines:
        deadline = fraction * full_sync

        ma = maturity_async(async_complete, deadline)
        ms = maturity_sync(sync_complete, deadline, cfg.branches)

        pa = predict(estimates, ma)
        ps = predict(estimates, ms)

        preds_async.append(pa)
        acc_async.append(float(np.mean(pa == y)))
        acc_sync.append(float(np.mean(ps == y)))
        depth_async.append(float(np.mean(ma)))
        depth_sync.append(float(np.mean(ms)))

    final_pred = preds_async[-1]
    early_index = int(np.argmin(np.abs(np.asarray(cfg.deadlines) - 0.10)))
    early_pred = preds_async[early_index]

    wrong_then_right = float(
        np.mean((early_pred != y) & (final_pred == y))
    )
    right_then_wrong = float(
        np.mean((early_pred == y) & (final_pred != y))
    )

    return {
        "acc_async": np.asarray(acc_async),
        "acc_sync": np.asarray(acc_sync),
        "depth_async": np.asarray(depth_async),
        "depth_sync": np.asarray(depth_sync),
        "wrong_then_right_async_10pct": np.asarray(wrong_then_right),
        "right_then_wrong_async_10pct": np.asarray(right_then_wrong),
    }


def run_regime(cfg: Config, *, fast_conflict: bool) -> dict[str, np.ndarray | float]:
    rows = [
        run_seed(seed, cfg, fast_conflict=fast_conflict)
        for seed in range(cfg.seeds)
    ]

    def stack(key: str) -> np.ndarray:
        return np.stack([np.asarray(row[key]) for row in rows], axis=0)

    acc_async = stack("acc_async")
    acc_sync = stack("acc_sync")
    depth_async = stack("depth_async")
    depth_sync = stack("depth_sync")

    x = np.asarray(cfg.deadlines)
    auc_async = float(np.trapezoid(acc_async.mean(axis=0), x))
    auc_sync = float(np.trapezoid(acc_sync.mean(axis=0), x))

    return {
        "mean_async": acc_async.mean(axis=0),
        "mean_sync": acc_sync.mean(axis=0),
        "sd_async": acc_async.std(axis=0),
        "sd_sync": acc_sync.std(axis=0),
        "mean_depth_async": depth_async.mean(axis=0),
        "mean_depth_sync": depth_sync.mean(axis=0),
        "auc_async": auc_async,
        "auc_sync": auc_sync,
        "wrong_then_right_async_10pct": float(
            np.mean([row["wrong_then_right_async_10pct"] for row in rows])
        ),
        "right_then_wrong_async_10pct": float(
            np.mean([row["right_then_wrong_async_10pct"] for row in rows])
        ),
    }


def nearest_index(values: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(values - target)))


def print_regime(name: str, result: dict[str, np.ndarray | float], cfg: Config) -> None:
    x = np.asarray(cfg.deadlines)
    chosen = (0.0, 0.10, 0.20, 0.25, 0.35, 0.50, 0.75, 1.00)

    print()
    print(name)
    print("=" * len(name))
    print(
        f"deadline-AUC  async={result['auc_async']:.4f}  "
        f"sync+early-exit={result['auc_sync']:.4f}"
    )
    print()
    print(
        f"{'deadline':>9s}  {'async acc':>10s}  {'sync acc':>10s}  "
        f"{'async depth':>11s}  {'sync depth':>10s}"
    )
    print("-" * 60)

    ma = np.asarray(result["mean_async"])
    ms = np.asarray(result["mean_sync"])
    da = np.asarray(result["mean_depth_async"])
    ds = np.asarray(result["mean_depth_sync"])

    for target in chosen:
        i = nearest_index(x, target)
        print(
            f"{x[i]:9.2f}  {ma[i]:10.4f}  {ms[i]:10.4f}  "
            f"{da[i]:11.3f}  {ds[i]:10.3f}"
        )

    print()
    print(
        "async at 10% deadline: wrong -> correct by final = "
        f"{result['wrong_then_right_async_10pct']:.4f}"
    )
    print(
        "async at 10% deadline: correct -> wrong by final = "
        f"{result['right_then_wrong_async_10pct']:.4f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=10_000)
    parser.add_argument("--seeds", type=int, default=10)
    args = parser.parse_args()

    cfg = Config(episodes=args.episodes, seeds=args.seeds)

    print("PresentMoment: deadline / partial-maturity scheduling sanity check")
    print(
        f"branches={cfg.branches} depth={cfg.depth} "
        f"episodes/seed={cfg.episodes} seeds={cfg.seeds}"
    )
    print(
        "SYNC control is generous: it has a readable early-exit head after every "
        "completed layer barrier."
    )

    neutral = run_regime(cfg, fast_conflict=False)
    conflict = run_regime(cfg, fast_conflict=True)

    print_regime("neutral evidence", neutral, cfg)
    print_regime("fast-channel conflict", conflict, cfg)

    print()
    print("Interpretation guardrail")
    print("------------------------")
    print(
        "This toy isolates the scheduling consequence of heterogeneous delays. "
        "It does not show that an asynchronous mesh learns better representations."
    )
    print(
        "The next gate must use trained computation and strong anytime/asynchronous "
        "controls under equal compute."
    )


if __name__ == "__main__":
    main()
