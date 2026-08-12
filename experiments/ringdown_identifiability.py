"""Characterize when a multiscale ringdown actually carries event age.

This replaces the easy 'five traces decode age' demo with an identifiability
calculation.  It is still a toy, but it asks the nontrivial question: how far
apart must the decay constants be, relative to measurement noise, before event
age can be separated from unknown event magnitude?

Model
-----
For channel i,

    z_i = A * g_i * exp(-age / tau_i) * lognormal_noise

Taking logs gives

    log(z_i/g_i) = log(A) - age / tau_i + eps_i

with eps_i ~ N(0, sigma^2).  The unknowns are theta=[log(A), age].  Their local
Fisher information is J.T @ R^-1 @ J, where

    J_i = [1, -1/tau_i].

If all tau_i are equal, the columns are linearly dependent: magnitude and age
are unidentifiable.  As the taus spread apart, the age Cramer-Rao bound falls.

Strict terminology note
-----------------------
This current-snapshot inverse problem is *not* by itself the standard
observability-Gramian problem.  The observability Gramian asks how well an
internal state can be reconstructed from an output trajectory.  Here the
internal bank is treated as the present measurement and we ask whether two
latent event parameters can be inferred from it.  Fisher/Jacobian conditioning
is the direct object.  Later closed-loop models can and should use ordinary
observability/controllability Gramians as appropriate.
"""

from __future__ import annotations

import math
import numpy as np


SEED = 7
N_EPISODES = 50_000
BASE_TAU_S = 30.0
LOG_NOISE_SD = 0.08
AGE_MAX_S = 600.0
LOG_AMPLITUDE_SD = 2.0

# Five channels are placed geometrically around BASE_TAU_S.
# ratio=1 means identical channels; larger ratios spread the temporal basis.
RATIOS = [1.0, 1.01, 1.02, 1.05, 1.10, 1.25, 1.50, 2.0, 4.0]


def tau_bank(ratio: float) -> np.ndarray:
    exponents = np.arange(-2, 3, dtype=float)
    return BASE_TAU_S * (float(ratio) ** exponents)


def fisher_metrics(taus: np.ndarray, sigma: float = LOG_NOISE_SD):
    # log(z/g) = log(A) - age/tau + epsilon
    J = np.column_stack([np.ones(len(taus)), -1.0 / taus])
    F = (J.T @ J) / (sigma * sigma)
    eig = np.linalg.eigvalsh(F)

    if eig[0] <= 1e-12:
        return math.inf, math.inf, 0.0

    cov_lower_bound = np.linalg.inv(F)
    age_sd_bound = math.sqrt(float(cov_lower_bound[1, 1]))
    condition = float(eig[-1] / eig[0])
    determinant = float(np.linalg.det(F))
    return age_sd_bound, condition, determinant


def monte_carlo_rmse(
    rng: np.random.Generator,
    taus: np.ndarray,
    sigma: float = LOG_NOISE_SD,
) -> float:
    # Under Gaussian log-noise the least-squares estimator is efficient here,
    # so this should closely track the Cramer-Rao age bound.
    X = np.column_stack([np.ones(len(taus)), -1.0 / taus])

    if np.linalg.matrix_rank(X) < 2:
        return math.inf

    pinv = np.linalg.pinv(X)
    age = rng.uniform(0.0, AGE_MAX_S, size=N_EPISODES)
    log_amplitude = rng.normal(0.0, LOG_AMPLITUDE_SD, size=N_EPISODES)
    noise = rng.normal(0.0, sigma, size=(N_EPISODES, len(taus)))

    y = log_amplitude[:, None] - age[:, None] / taus[None, :] + noise
    beta_hat = y @ pinv.T
    age_hat = beta_hat[:, 1]
    return float(np.sqrt(np.mean((age_hat - age) ** 2)))


def main() -> None:
    rng = np.random.default_rng(SEED)

    print("PresentMoment: ringdown identifiability")
    print(f"channels=5  base tau={BASE_TAU_S:g}s  log-noise sigma={LOG_NOISE_SD:g}")
    print(f"Monte Carlo episodes per row={N_EPISODES}")
    print()
    print(
        f"{'ratio':>7s}  {'tau bank (s)':38s}  "
        f"{'CRLB age SD':>12s}  {'MC RMSE':>10s}  {'Fisher cond':>12s}"
    )
    print("-" * 100)

    for ratio in RATIOS:
        taus = tau_bank(ratio)
        bound, condition, _ = fisher_metrics(taus)
        rmse = monte_carlo_rmse(rng, taus)

        tau_text = "[" + ", ".join(f"{x:.2f}" for x in taus) + "]"
        bound_text = "singular" if not math.isfinite(bound) else f"{bound:10.3f}s"
        rmse_text = "singular" if not math.isfinite(rmse) else f"{rmse:8.3f}s"
        cond_text = "inf" if not math.isfinite(condition) else f"{condition:12.1f}"

        print(
            f"{ratio:7.2f}  {tau_text:38s}  "
            f"{bound_text:>12s}  {rmse_text:>10s}  {cond_text:>12s}"
        )

    print()
    print("Interpretation:")
    print("  * identical decay rates are singular: age and magnitude are the same direction;")
    print("  * nearly identical rates are technically identifiable but catastrophically ill-conditioned;")
    print("  * temporal diversity, not merely channel count, creates usable age information;")
    print("  * the noise floor sets how much separation is practically enough.")
    print()
    print("This characterizes the synthetic temporal basis; it is not evidence that")
    print("real interoceptive systems decode event age this way.")


if __name__ == "__main__":
    main()
