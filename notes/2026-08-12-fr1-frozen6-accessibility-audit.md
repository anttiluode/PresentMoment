# Frozen-six FR1 lagged accessibility audit

Date: 2026-08-12

This note continues `2026-08-12-geometric-deerskin-time-audit.md` after the ChatGPT delivery timeout.

## Question

Does the already-frozen, anatomy-selected six-subject FR1 cohort show a systematic difference in how much trial-specific source history remains useful to a receiver in delta/theta versus beta, after subtracting a condition-matched trial-mismatch null?

The estimator was frozen before this six-subject outcome was read:

- bipolar human iEEG;
- anatomically selected same-hemisphere hippocampus/parietal pair;
- analytic-band state;
- target predicted from fixed target self-history;
- one source lag added at 10, 20, 40, 80, 120, 160, 240, 320, 480, 640 ms;
- whole-trial cross-validation;
- source trials mismatched to target trials within condition to preserve marginal spectrum/autocorrelation and event timing while breaking trial-specific pairing;
- load-bearing quantity = observed prediction increment minus mismatch mean.

Frozen cohort: R1066P/1, R1035M/0, R1125T/2, R1053M/0, R1113T/0, R1106M/1.

## Plumbing failure and fix

The first frozen-six workflow failed because the generic OpenNeuro sidecar URL assumed one BIDS layout and returned 404. `fr1_lagged_accessibility_v2.py` reuses the S3 key resolver already validated in `fr1_multi_subject_pte_v2.py`. This changes metadata discovery only; cohort, anatomy selection, estimator, lags and null are unchanged.

## v1 aggregate: apparently striking, but wrong statistic for band comparison

The first aggregate summarized each profile with `far_240ms_plus_area_r2_ms` from `profile_summary()`.

That quantity integrates only `max(excess, 0)`. It is useful descriptively for asking where positive excess exists inside one profile, but it is unsuitable for comparing two bands because a noisier / higher-variance zero-centered band can acquire a larger positive-only area simply by fluctuating more.

Using that positive-clipped area produced an enticing result: beta exceeded delta/theta in all six participants, with an exact sign-flip p = 0.03125.

That result must NOT be interpreted biologically. The statistic rewards positive excursions and discards negative ones.

## v2 signed reaggregate

The correction integrates the signed mismatch-subtracted excess directly over the far-history lags 240, 320, 480 and 640 ms:

    signed_far_area = integral excess_delta_R2(lag) dlag

Then, for each participant, it averages across encoding/recall and both directions and computes delta/theta minus beta.

Participant contrasts:

- R1035M: +0.0011325
- R1053M: +0.0007779
- R1066P: -0.0012989
- R1106M: +0.0011665
- R1113T: -0.0015006
- R1125T: -0.0030317

Group summary:

- mean delta/theta minus beta signed far-area: -0.0004590
- median: -0.0002605
- 3/6 positive
- exact two-sided sign-flip p = 0.5625

No individual lag showed a clean cohort effect. The closest exploratory point was 160 ms: 5/6 participants had delta/theta > beta, exact sign-flip p = 0.09375. Nothing should be made of that without a new frozen replication.

## Verdict

The frozen-six data do **not** support a clean ordering such as:

- “low frequencies expose a deeper recoverable history than beta”, or
- the accidental v1 reversal, “beta exposes deeper history than low frequencies”.

The v1 all-six beta result was produced by positive clipping. Signed integration removes it.

This is a useful negative result and a useful audit result. The temporal-accessibility framework survives, but this particular simple single-lag ridge estimator does not establish a frequency hierarchy of history depth in this cohort.

## Consequences for PresentMoment

1. Do not equate slow autocorrelation with accessible past.
2. Do not define a history horizon from positive-only area or threshold crossings without controlling estimator variance.
3. Any future accessibility metric should be signed or otherwise calibrated against its full null distribution.
4. “Temporal accessibility” remains a receiver/readout property: which source history improves prediction beyond the receiver’s own state and beyond condition-matched marginal dynamics.
5. The next cleaner empirical branch is the Alzheimer raw-data primitive: test band-specific spatial-mode switching/self-transition directly against spectrum-preserving nulls, rather than retesting derived vocabulary/dwell/criticality summaries.
6. The repaired RepOD geometry hint remains only a sign-consistent exploratory effect; freeze one definition before any independent schizophrenia replication.

## Conceptual residue

The old Geometric-Neuron / Deerskin / Pribram material was useful as noise because it pushed the question away from “where is time stored?” toward:

> At a given instant, which distributed degrees of freedom are readable by a particular receiver, under a particular routing/phase state, and how far into prior source state does that readout remain informative above the receiver’s own dynamics?

That is the live idea. The specific frequency ordering has not earned itself.
