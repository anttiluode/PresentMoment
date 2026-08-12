"""Passive lag cannot identify the mechanism that generated a temporal frontier.

This is a deliberately tiny negative/identifiability control motivated by the
PerceptionLab wave calibration and Yang et al. (Nature Communications, 2026).

Two mechanisms are constructed to have the same receiver observations:

A. sequential propagation along a chain
B. one common broadcast whose receivers have matched response delays

For passive observation, both give

    y_i(t) = u(t - d_i)

so every trace and every pairwise lag is exactly identical.  A lag surface therefore
identifies an *effective temporal frontier*, not the microscopic carrier.

The mechanisms become distinguishable only after an intervention.  Cutting the chain
between receiver 1 and 2 prevents the event from reaching downstream propagation
receivers, while a common broadcast continues to reach them.

This is standard causal/system-identification logic, not a novelty claim.

Run:
    python experiments/frontier_mechanism_aliasing.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    name: str
    traces: tuple[tuple[int, ...], ...]


def impulse(length: int, at: int = 3) -> list[int]:
    x = [0] * length
    x[at] = 1
    return x


def delay_signal(x: list[int], delay: int) -> tuple[int, ...]:
    out = [0] * len(x)
    for t, value in enumerate(x):
        j = t + int(delay)
        if j < len(out):
            out[j] = value
    return tuple(out)


def propagation_chain(x: list[int], edge_delays: tuple[int, ...], cut_after: int | None = None) -> Observation:
    """Source -> R0 -> R1 -> ...; receiver i accumulates preceding edge delays."""
    cumulative = 0
    traces = []
    for i, edge_delay in enumerate(edge_delays):
        cumulative += edge_delay
        if cut_after is not None and i > cut_after:
            traces.append(tuple([0] * len(x)))
        else:
            traces.append(delay_signal(x, cumulative))
    return Observation("sequential propagation", tuple(traces))


def delayed_broadcast(x: list[int], receiver_delays: tuple[int, ...]) -> Observation:
    """One common source reaches each receiver through its own response/path delay."""
    return Observation(
        "common broadcast + receiver delays",
        tuple(delay_signal(x, d) for d in receiver_delays),
    )


def peak_time(trace: tuple[int, ...]) -> int | None:
    try:
        return trace.index(1)
    except ValueError:
        return None


def pairwise_lags(obs: Observation) -> dict[tuple[int, int], int | None]:
    peaks = [peak_time(t) for t in obs.traces]
    out: dict[tuple[int, int], int | None] = {}
    for i in range(len(peaks)):
        for j in range(i + 1, len(peaks)):
            if peaks[i] is None or peaks[j] is None:
                out[(i, j)] = None
            else:
                out[(i, j)] = peaks[j] - peaks[i]
    return out


def main() -> None:
    x = impulse(48, at=3)
    edge_delays = (2, 3, 4, 5)

    # Propagation receiver delays are cumulative: 2, 5, 9, 14.
    receiver_delays = tuple(
        sum(edge_delays[: i + 1]) for i in range(len(edge_delays))
    )

    wave = propagation_chain(x, edge_delays)
    broadcast = delayed_broadcast(x, receiver_delays)

    print("PresentMoment: frontier mechanism aliasing")
    print(f"effective receiver delays: {receiver_delays}")
    print()

    assert wave.traces == broadcast.traces
    assert pairwise_lags(wave) == pairwise_lags(broadcast)

    print("PASSIVE OBSERVATION")
    print("  traces identical:       ", wave.traces == broadcast.traces)
    print("  pairwise lags identical:", pairwise_lags(wave) == pairwise_lags(broadcast))
    print("  lags:", pairwise_lags(wave))
    print()
    print("  => lag/frontier is observable; carrier mechanism is not identifiable here.")
    print()

    # Cut after receiver index 1: downstream receivers 2 and 3 cannot be reached
    # in the sequential chain. The common broadcast has no such intermediate edge.
    wave_cut = propagation_chain(x, edge_delays, cut_after=1)
    broadcast_same = delayed_broadcast(x, receiver_delays)

    print("INTERVENTION: cut propagation path after receiver 1")
    print("  propagation peak times:", [peak_time(t) for t in wave_cut.traces])
    print("  broadcast peak times:  ", [peak_time(t) for t in broadcast_same.traces])
    assert wave_cut.traces != broadcast_same.traces
    assert peak_time(wave_cut.traces[2]) is None
    assert peak_time(broadcast_same.traces[2]) is not None
    print("  mechanisms now distinguishable: True")
    print()
    print("Guardrail:")
    print("  A measured delay gradient supports an effective temporal frontier.")
    print("  It does not, by itself, prove local physical propagation between receivers.")
    print("  Distinguishing carriers requires interventions or additional mechanistic data.")


if __name__ == "__main__":
    main()
