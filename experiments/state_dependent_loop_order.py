"""When does state modulation escape a fixed exponential bank?

A fixed linear bank can be diagonalised into independent exponential modes.
Merely changing each mode's decay rate over time does not necessarily restore a
special geometry if all state-dependent transition operators share the same
basis and commute.

The stronger escape is *state-dependent coupling*: the transition operator in
one physiological state does not commute with the operator in another state.
Then equal amounts of two states can produce different present states depending
on order.

This is a structural sanity check, not a novelty claim.  Switched and bilinear
systems are standard control theory.  The point is to state exactly what kind
of state dependence would evade the fixed-modal collapse used elsewhere in the
project family.
"""

from __future__ import annotations

import numpy as np


X0 = np.array([1.0, 0.2])

# Calm dynamics: two uncoupled fading modes.
T_CALM = np.diag([0.96, 0.80])

# 'Danger' that only changes rates in the same basis.  Still commuting.
T_DANGER_RATES_ONLY = np.diag([0.80, 0.95])

# 'Danger' that also changes coupling between modes.  Stable, but not
# simultaneously diagonal with T_CALM.
T_DANGER_COUPLED = np.array(
    [
        [0.78, 0.25],
        [0.04, 0.90],
    ],
    dtype=float,
)


def apply(sequence: str, danger: np.ndarray) -> np.ndarray:
    x = X0.copy()
    for symbol in sequence:
        T = T_CALM if symbol == "C" else danger
        x = T @ x
    return x


def commutator_norm(A: np.ndarray, B: np.ndarray) -> float:
    return float(np.linalg.norm(A @ B - B @ A))


def order_gap(seq_a: str, seq_b: str, danger: np.ndarray) -> float:
    return float(np.linalg.norm(apply(seq_a, danger) - apply(seq_b, danger)))


def report(name: str, danger: np.ndarray) -> None:
    print(name)
    print(f"  spectral radius danger = {max(abs(np.linalg.eigvals(danger))):.6f}")
    print(f"  ||[C,D]||             = {commutator_norm(T_CALM, danger):.8f}")

    for a, b in [("CD", "DC"), ("CCDD", "DDCC"), ("CDCD", "DCDC")]:
        xa = apply(a, danger)
        xb = apply(b, danger)
        print(
            f"  {a:4s} vs {b:4s} gap={np.linalg.norm(xa-xb):.8f}  "
            f"{a}->{np.round(xa, 6)}  {b}->{np.round(xb, 6)}"
        )
    print()


def main() -> None:
    print("PresentMoment: state-dependent loop order")
    print(f"initial state = {X0}")
    print()

    report("rates-only modulation (same modal basis)", T_DANGER_RATES_ONLY)
    report("coupling modulation (noncommuting basis)", T_DANGER_COUPLED)

    print("Interpretation:")
    print("  rates-only modulation changes persistence but preserves order-independence;")
    print("  coupling modulation makes the current state depend on the path through states;")
    print("  therefore 'A changes with danger' is only structurally interesting when")
    print("  the family of A/T operators is not reducible to one shared modal basis.")


if __name__ == "__main__":
    main()
