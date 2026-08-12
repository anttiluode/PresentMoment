# R1022J trial-level check: delta/theta survives, beta does not

Date: 2026-08-12

This note hardens the first real human-iEEG calibration in
`FR1_REAL_IEEG_CALIBRATION.md`.

The first pass compared aggregate Phase Transfer Entropy (PTE) direction to time-shuffled
phase surrogates.  That was useful as a phase-relationship null, but averaging many
trials made the surrogate directional distribution extremely narrow.  Even the tiny beta
asymmetry therefore acquired a misleadingly dramatic surrogate z-score.

The follow-up deliberately asks a harsher within-recording question:

> Across individual trials, is `PTE(HIPP -> angular)` systematically different from
> `PTE(angular -> HIPP)`?

For each trial we compute the paired difference and paired directional index, then use:

```text
50,000 random sign-flip permutations of the paired PTE difference
20,000 bootstrap resamples of trial directional index
Wilcoxon signed-rank as a rank-based descriptive cross-check
```

This is still **one participant**.  Trials from one participant are not independent
participants, so none of these p-values is population-level evidence.

---

## Delta-theta 0.5-8 Hz

Published group-level direction:

```text
hippocampus -> parietal
```

### Successful encoding

```text
trials                              80
mean HIPP -> angular PTE            1.41674 bits
mean angular -> HIPP PTE            1.33683 bits
paired PTE difference              +0.07990 bits
paired effect dz                   +0.326
mean trial direction index         +0.02986
bootstrap 95% CI                    [+0.01035, +0.04970]
sign-flip p                          0.00448
Wilcoxon p                           0.00549
trials in published direction       62.5%
```

The low-frequency encoding direction survives the trial-level check.

### Recall

```text
trials                              85
mean HIPP -> angular PTE            1.40493 bits
mean angular -> HIPP PTE            1.25510 bits
paired PTE difference              +0.14983 bits
paired effect dz                   +0.657
mean trial direction index         +0.05631
bootstrap 95% CI                    [+0.03702, +0.07602]
sign-flip p                         < 0.00002
Wilcoxon p                           1.78e-7
trials in published direction       77.65%
```

The recall asymmetry is stronger in this recording and survives every paired descriptive
check used here.

---

## Beta 12-30 Hz

Published group-level direction:

```text
parietal -> hippocampus
```

The aggregate mean in R1022J happened to have that sign during both encoding and recall.
The trial-level check shows why the sign alone must not be oversold.

### Successful encoding

```text
trials                              80
mean HIPP -> angular PTE            0.90429 bits
mean angular -> HIPP PTE            0.91468 bits
paired PTE difference              -0.01038 bits
paired effect dz                   -0.082
mean trial direction index         -0.00668
bootstrap 95% CI                    [-0.02197, +0.00848]
sign-flip p                          0.461
Wilcoxon p                           0.407
trials in published direction       51.25%
```

### Recall

```text
trials                              85
mean HIPP -> angular PTE            0.89203 bits
mean angular -> HIPP PTE            0.90145 bits
paired PTE difference              -0.00942 bits
paired effect dz                   -0.066
mean trial direction index         -0.00511
bootstrap 95% CI                    [-0.02267, +0.01175]
sign-flip p                          0.543
Wilcoxon p                           0.939
trials in published direction       45.88%
```

So beta **does not survive** a trial-level within-recording inference in this subject.
Its mean sign matches the published group result, but the trial distribution is entirely
compatible with zero directional bias.

---

## Revised verdict on the first real-data calibration

The earlier shorthand

```text
4/4 predicted signs matched
```

remains arithmetically true but is no longer the scientifically useful summary.

The better summary is:

> **In one anatomically clean hippocampus-angular bipolar pair, the published
> hippocampus -> parietal delta/theta direction is reproducible within trials during
> both successful encoding and recall; the published reverse beta direction appears
> only as a tiny aggregate sign and is not reliable across trials.**

This is exactly why the harder check was needed.

It prevents a calibration coincidence from being mistaken for a full spectral
replication.

---

## What this changes next

The expansion should not demand that every individual participant reproduce every
population-level beta sign.  Instead we should carry the actual participant-level
continuous directional indices into a small replication cohort and ask:

```text
1. Is delta/theta HIPP -> parietal direction consistently positive across subjects?
2. Is beta shifted in the opposite direction at the group level even if weak per subject?
3. Does the frequency contrast
       DI_delta_theta - DI_beta
   replicate more robustly than either band alone?
```

That third contrast may be the most faithful target because the published result is a
**frequency-specific feedback loop**, not a claim that every single beta trial is
strongly top-down.

Only after the basic frequency contrast behaves sensibly across independently selected
participants should PresentMoment condition it on travelling-wave state, arousal, or
other candidate `accessibility operator` variables.

---

## Reproducibility

Code:

```text
experiments/fr1_pte_trial_stats.py
```

GitHub Actions run:

```text
31591894748
```

Artifact:

```text
fr1-pte-r1022j-trial-stats
```
