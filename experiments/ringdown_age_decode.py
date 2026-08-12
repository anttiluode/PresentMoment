"""Can a multiscale ringdown encode *when* an event happened?

This is a mechanism sanity check for PresentMoment, not a biological model and
not evidence that the body actually performs this decoding.

Setup
-----
Each synthetic episode contains one past perturbation.  At the present instant
its external cause is gone.  The event had an unknown magnitude A and occurred
`age` seconds ago.

A body channel with relaxation constant tau contains

    b_i = A * g_i * exp(-age / tau_i) * noise

A single channel confounds event magnitude with event age.  With multiple
relaxation constants, the common unknown magnitude can in principle be
separated from the differential decay across channels.

The experiment fits only a linear ridge readout to log channel amplitudes.
It compares:

* a single 30 s trace;
* a single 120 s trace;
* all five ringdown channels;
* an oracle control: one 30 s trace plus the true event magnitude.

The multiscale result is expected from the construction.  Its purpose is to
make the proposed physical temporal basis explicit and falsifiable before we
build anything more complicated.
"""

from __future__ import annotations

import numpy as np


SEED = 42
N_EPISODES = 12_000
N_TRAIN = 8_000
MAX_AGE_S = 600.0

# Deliberately broad event-intensity distribution.  This makes a single decay
# trace ambiguous: a large old event can resemble a smaller recent event.
LOG_AMPLITUDE_SD = 2.0
MEASUREMENT_LOG_NOISE_SD = 0.08

TAUS_S = np.array([2.0, 8.0, 30.0, 120.0, 600.0])
GAINS = np.array([1.00, 0.85, 1.10, 0.90, 1.05])

RIDGE_ALPHA = 1e-3
EPS = 1e-12


def make_data(rng: np.random.Generator):
    age = rng.uniform(0.5, MAX_AGE_S, size=N_EPISODES)
    amplitude = np.exp(rng.normal(0.0, LOG_AMPLITUDE_SD, size=N_EPISODES))

    body = (
        amplitude[:, None]
        * GAINS[None, :]
        * np.exp(-age[:, None] / TAUS_S[None, :])
    )

    # Positive multiplicative measurement noise keeps the log representation
    # simple while preventing an unrealistically exact algebraic inversion.
    body *= np.exp(
        rng.normal(0.0, MEASUREMENT_LOG_NOISE_SD, size=body.shape)
    )
    body += EPS

    return age, amplitude, body


def ridge_metrics(
    X: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
):
    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]

    mu = X_train.mean(axis=0)
    sd = X_train.std(axis=0) + 1e-9

    X_train = (X_train - mu) / sd
    X_test = (X_test - mu) / sd

    X_train = np.column_stack([np.ones(len(X_train)), X_train])
    X_test = np.column_stack([np.ones(len(X_test)), X_test])

    reg = RIDGE_ALPHA * np.eye(X_train.shape[1])
    reg[0, 0] = 0.0

    w = np.linalg.solve(
        X_train.T @ X_train + reg,
        X_train.T @ y_train,
    )
    pred = X_test @ w

    mae = float(np.mean(np.abs(pred - y_test)))
    ss_res = float(np.sum((pred - y_test) ** 2))
    ss_tot = float(np.sum((y_test - y_test.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot
    return mae, r2


def main() -> None:
    rng = np.random.default_rng(SEED)
    age, amplitude, body = make_data(rng)

    order = rng.permutation(N_EPISODES)
    train_idx = order[:N_TRAIN]
    test_idx = order[N_TRAIN:]

    log_body = np.log(body)

    conditions = {
        "single_30s": log_body[:, [2]],
        "single_120s": log_body[:, [3]],
        "multiscale_5": log_body,
        "oracle_30s_plus_true_magnitude": np.column_stack(
            [log_body[:, 2], np.log(amplitude)]
        ),
    }

    print("PresentMoment: somatic ringdown age-decoding sanity test")
    print(f"episodes={N_EPISODES}  age range=0.5..{MAX_AGE_S:.0f} s")
    print(f"tau bank={TAUS_S.tolist()} s")
    print(f"unknown event log-amplitude SD={LOG_AMPLITUDE_SD}")
    print()
    print(f"{'condition':34s} {'MAE (s)':>10s} {'R^2':>10s}")
    print("-" * 58)

    for name, X in conditions.items():
        mae, r2 = ridge_metrics(X, age, train_idx, test_idx)
        print(f"{name:34s} {mae:10.3f} {r2:10.4f}")

    print()
    print("Interpretation:")
    print(
        "  Several differently decaying traces can separate event age from "
        "unknown event magnitude."
    )
    print(
        "  This is built into the synthetic dynamics; it demonstrates a "
        "possible temporal basis, not a biological result."
    )
    print(
        "  The next nontrivial test is whether a closed-loop synthetic body "
        "adds anything over a parameter-matched recurrent baseline."
    )


if __name__ == "__main__":
    main()
