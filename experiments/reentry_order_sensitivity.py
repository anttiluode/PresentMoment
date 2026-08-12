"""Order-sensitivity gate for active re-entry.

The point is to prevent a bad generalization:

    "order appeared several times, therefore order itself is a fundamental variable"

KYY already supplied a counterexample where monotone temporal order did not help after
contiguity was controlled. The stronger condition is *order sensitivity*: swapping the
same constituent transitions must change receiver accessibility.

This known-answer gate sweeps two 3-D rotations. It compares:
  - commutator norm ||AB - BA||_F
  - loss of the fixed receiver's label signal when inverse actions are replayed in the
    wrong order.

It also includes a commuting control using two rotations about the same axis.

Run:
    python experiments/reentry_order_sensitivity.py
"""
from __future__ import annotations

import math
import numpy as np


def rx(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def rz(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


E_X = np.array([1.0, 0.0, 0.0])


def wrong_order_gain(A: np.ndarray, B: np.ndarray) -> float:
    """Encoding B@A, then wrong inverse action order A^-1 followed by B^-1."""
    hidden = B @ A @ E_X
    wrong = B.T @ A.T @ hidden
    return float(E_X @ wrong)


def correct_gain(A: np.ndarray, B: np.ndarray) -> float:
    hidden = B @ A @ E_X
    correct = A.T @ B.T @ hidden
    return float(E_X @ correct)


def main() -> None:
    angles = np.deg2rad(np.linspace(0.0, 90.0, 10))
    commutators: list[float] = []
    penalties: list[float] = []

    for a in angles:
        for b in angles:
            A = rz(float(a))
            B = rx(float(b))
            comm = float(np.linalg.norm(A @ B - B @ A, ord="fro"))
            cg = correct_gain(A, B)
            wg = wrong_order_gain(A, B)
            assert abs(cg - 1.0) < 1e-12
            penalty = 1.0 - wg
            commutators.append(comm)
            penalties.append(penalty)

    corr = float(np.corrcoef(commutators, penalties)[0, 1])

    # Commuting control: same-axis rotations.
    commuting_penalties = []
    commuting_commutators = []
    for a in angles:
        for b in angles:
            A = rz(float(a))
            B = rz(float(b))
            commuting_commutators.append(
                float(np.linalg.norm(A @ B - B @ A, ord="fro"))
            )
            commuting_penalties.append(1.0 - wrong_order_gain(A, B))

    print("PresentMoment: order-sensitivity gate")
    print()
    print("noncommuting sweep: Rz(a), Rx(b), a,b in 0..90 deg")
    print(f"  grid points                         : {len(commutators)}")
    print(f"  corr(commutator norm, order penalty): {corr:+.6f}")
    print(f"  max commutator norm                 : {max(commutators):.6f}")
    print(f"  max wrong-order signal penalty      : {max(penalties):.6f}")
    print()
    print("commuting control: Rz(a), Rz(b)")
    print(f"  max commutator norm                 : {max(commuting_commutators):.3e}")
    print(f"  max wrong-order signal penalty      : {max(abs(x) for x in commuting_penalties):.3e}")
    print()

    assert corr > 0.9
    assert max(commuting_commutators) < 1e-12
    assert max(abs(x) for x in commuting_penalties) < 1e-12

    print("Interpretation:")
    print("  * order is not generically informative;")
    print("  * order matters here because the transition composition is path-sensitive;")
    print("  * when the same operations commute, swapping them changes nothing;")
    print("  * the empirical brain/AI question should therefore be counterfactual:")
    print("      same constituents, different order -> different future accessibility?")
    print("  * this is a mathematical calibration, not evidence that neural recall uses rotations.")


if __name__ == "__main__":
    main()
