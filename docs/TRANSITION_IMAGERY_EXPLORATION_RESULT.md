# Transition imagery gate — exploration result

## Status

Exploration/instrument set only.  This document was committed while the frozen held-out
workflow was still running.  These subjects are **not** the hypothesis test.

Preregistration: `docs/TRANSITION_IMAGERY_GATE.md`.

Subjects:

```text
S01 S02 S03 S04 S06 S07
```

The assay and channel groups were not changed after seeing these numbers.

---

## Result

Frozen cross-posture transition-vs-static motor-imagery assay:

```text
sensorimotor mean balanced accuracy    0.50963
bootstrap 95% CI                      [0.45035, 0.55796]
subjects > 0.5                         4 / 6

occipital mean balanced accuracy       0.52999
bootstrap 95% CI                      [0.48459, 0.57516]
subjects > 0.5                         4 / 6

sensorimotor - occipital              -0.02036
bootstrap 95% CI                      [-0.09827, 0.05475]
sign-flip p, two-sided                 0.65709
subjects with positive difference      2 / 6
```

Per subject:

```text
       sensorimotor   occipital
S01       0.5750       0.4563
S02       0.5125       0.4625
S03       0.4708       0.5100
S04       0.3813       0.5750
S06       0.5472       0.5667
S07       0.5708       0.6100
```

Workflow run: `31686117490`.
Artifact: `9175546106`.

---

## Interpretation allowed at this stage

The code/data path works:

- all four imagery conditions are present;
- the frozen 0.5–3.0 s window is valid;
- cross-posture training/testing runs without class imbalance or missing channels;
- both frozen sensorimotor and occipital feature groups produce finite subject-level
  scores.

The exploration numbers do **not** support a sensorimotor advantage.  If anything the
point estimate is in the opposite direction.

That is not yet a confirmatory null because these subjects were explicitly reserved for
instrument verification.

Crucially, this result gives no reason to tune:

```text
bands
window
classifier
channels
thresholds
```

before the held-out gate.

Doing so would destroy the point of the preregistration.

The held-out workflow therefore runs the assay unchanged on `S08`–`S23`.
