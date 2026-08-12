#!/usr/bin/env python3
"""
Active re-entry gate
====================

A deliberately tiny systems toy for PresentMoment.

Question
--------
Can a memory-bearing latent state be physically present but unreadable by the current
receiver, then become readable because the system executes the right control trajectory?

This is NOT a brain model. It is a known-answer construction that separates:

    trace exists
    trace is readable now
    trace can be made readable by a chosen trajectory

The construction uses a 3-D state and a fixed one-dimensional receiver y = x[0].

Encoding hides the item label in the z axis with two non-commuting rotations:

    visible x-axis
      -- Rz(+90deg) --> y-axis
      -- Rx(+90deg) --> z-axis

The current receiver therefore sees no label information.

A correct re-entry trajectory retraces those state transitions in reverse:

    Rx(-90deg) then Rz(-90deg)

and returns the label to the receiver-potent x axis.

A scrambled trajectory uses exactly the same two inverse actions in the wrong order.
Because the rotations do not commute, the label remains receiver-null.

A second known-answer control shows periodic accessibility: if the hidden z-state is
allowed to rotate autonomously in the x-z plane, the same fixed readout alternates
between blind and informative phases.

Run:
    python experiments/active_reentry_gate.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import numpy as np


def rx(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array(
        [[1.0, 0.0, 0.0],
         [0.0, c, -s],
         [0.0, s, c]],
        dtype=float,
    )


def ry(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array(
        [[c, 0.0, s],
         [0.0, 1.0, 0.0],
         [-s, 0.0, c]],
        dtype=float,
    )


def rz(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array(
        [[c, -s, 0.0],
         [s, c, 0.0],
         [0.0, 0.0, 1.0]],
        dtype=float,
    )


@dataclass
class ReadoutStats:
    accuracy: float
    separation: float
    dprime: float


def readout_stats(states: np.ndarray, labels: np.ndarray) -> ReadoutStats:
    """Read only x[0], then score sign decoding and Gaussian d' separation."""
    y = states[:, 0]
    pred = np.where(y >= 0.0, 1.0, -1.0)
    accuracy = float(np.mean(pred == labels))

    pos = y[labels > 0]
    neg = y[labels < 0]
    separation = float(pos.mean() - neg.mean())

    pooled = math.sqrt(
        0.5 * (float(pos.var(ddof=1)) + float(neg.var(ddof=1)))
    )
    dprime = separation / pooled if pooled > 0.0 else float("inf")
    return ReadoutStats(accuracy, separation, dprime)


def apply(transform: np.ndarray, states: np.ndarray) -> np.ndarray:
    return (transform @ states.T).T


def run_reentry_gate(
    n_trials: int = 20_000,
    sigma: float = 0.35,
    seed: int = 7,
) -> dict[str, ReadoutStats | float | np.ndarray]:
    rng = np.random.default_rng(seed)

    # Two non-commuting state transitions.
    A = rz(math.pi / 2.0)
    B = rx(math.pi / 2.0)

    visible_axis = np.array([1.0, 0.0, 0.0], dtype=float)

    # Execute A then B during "encoding".
    hidden_axis = B @ A @ visible_axis

    labels = rng.choice(np.array([-1.0, 1.0]), size=n_trials)
    states = labels[:, None] * hidden_axis[None, :]
    states += rng.normal(0.0, sigma, size=states.shape)

    # Starting from hidden state:
    # correct execution order = B^-1 then A^-1
    # aggregate column-vector transform = A^-1 @ B^-1
    correct = A.T @ B.T

    # Same two inverse actions, wrong order = A^-1 then B^-1
    wrong_order = B.T @ A.T

    # Only the first re-entry action.
    partial = B.T

    return {
        "commutator_norm": float(np.linalg.norm(A @ B - B @ A)),
        "hidden_axis": hidden_axis,
        "static": readout_stats(states, labels),
        "partial": readout_stats(apply(partial, states), labels),
        "correct_reentry": readout_stats(apply(correct, states), labels),
        "wrong_order": readout_stats(apply(wrong_order, states), labels),
    }


def run_wait_for_loop(
    n_trials: int = 20_000,
    sigma: float = 0.35,
    seed: int = 11,
    phase_step_deg: float = 15.0,
    steps: int = 24,
) -> list[ReadoutStats]:
    """
    Put the label in hidden z and let an autonomous x-z rotation carry it repeatedly
    through the fixed x readout.

    This is the smallest possible toy for:
        "the trace is there, but perhaps the receiver has to catch the right phase."
    """
    rng = np.random.default_rng(seed)
    labels = rng.choice(np.array([-1.0, 1.0]), size=n_trials)

    hidden_axis = np.array([0.0, 0.0, 1.0], dtype=float)
    states = labels[:, None] * hidden_axis[None, :]
    states += rng.normal(0.0, sigma, size=states.shape)

    step_matrix = ry(math.radians(phase_step_deg))
    out: list[ReadoutStats] = []

    cur = states.copy()
    for _ in range(steps + 1):
        out.append(readout_stats(cur, labels))
        cur = apply(step_matrix, cur)
    return out


def _fmt(stats: ReadoutStats) -> str:
    return (
        f"accuracy={stats.accuracy:0.4f}  "
        f"separation={stats.separation:+0.4f}  "
        f"d'={stats.dprime:+0.3f}"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20_000)
    ap.add_argument("--sigma", type=float, default=0.35)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--phase-step-deg", type=float, default=15.0)
    ap.add_argument("--loop-steps", type=int, default=24)
    args = ap.parse_args()

    result = run_reentry_gate(
        n_trials=args.trials,
        sigma=args.sigma,
        seed=args.seed,
    )

    print("ACTIVE RE-ENTRY GATE")
    print("--------------------")
    print(f"hidden axis       : {np.asarray(result['hidden_axis'])}")
    print(f"||AB - BA||_F     : {result['commutator_norm']:.6f}")
    print(f"static            : {_fmt(result['static'])}")
    print(f"partial re-entry  : {_fmt(result['partial'])}")
    print(f"correct re-entry  : {_fmt(result['correct_reentry'])}")
    print(f"wrong action order: {_fmt(result['wrong_order'])}")

    loop = run_wait_for_loop(
        n_trials=args.trials,
        sigma=args.sigma,
        seed=args.seed + 1,
        phase_step_deg=args.phase_step_deg,
        steps=args.loop_steps,
    )

    best_i = int(np.argmax([s.accuracy for s in loop]))
    print()
    print("WAIT-FOR-THE-LOOP CONTROL")
    print("-------------------------")
    print(
        f"phase step={args.phase_step_deg:g} deg; "
        f"best step={best_i}; "
        f"phase~{best_i * args.phase_step_deg:g} deg"
    )
    for i, stats in enumerate(loop):
        if i in {0, best_i, args.loop_steps // 2, args.loop_steps}:
            print(
                f"step {i:2d}  phase~{i * args.phase_step_deg:6.1f} deg  "
                f"{_fmt(stats)}"
            )

    print()
    print("Interpretation:")
    print("  * The label-bearing state exists in all four re-entry conditions.")
    print("  * A fixed receiver is initially blind to it.")
    print("  * The correct control trajectory makes it output-potent.")
    print("  * The same actions in the wrong order do not.")
    print("  * In the autonomous-loop control, readability is periodic.")
    print("  * This is a systems sanity check, not evidence for a neural mechanism.")


if __name__ == "__main__":
    main()
