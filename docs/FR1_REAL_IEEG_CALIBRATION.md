# First real human-iEEG calibration: hippocampus <-> angular gyrus PTE

Date: 2026-08-12

This note records the first `PresentMoment` analysis run on **real public human intracranial EEG** rather than a synthetic dynamical system.

It is a **calibration / method sanity check**, not a new biological result and not a replication study.

The goal was deliberately conservative:

> Before testing the new state-dependent temporal-accessibility hypothesis, can our open-data + GitHub Actions pipeline recover the **qualitative frequency-dependent direction signature already reported in the same UPENN-RAM free-recall family**?

The first one-subject / one-pair answer was **yes: 4/4 predicted directional signs matched**.

That earns expansion to more subjects. It does not earn the new hypothesis yet.

---

## 1. Published calibration target

Das & Menon (Cerebral Cortex 2024, DOI `10.1093/cercor/bhae287`) analyzed bipolar UPENN-RAM intracranial EEG during verbal/spatial episodic-memory tasks using **Phase Transfer Entropy (PTE)**.

Their group-level qualitative result was frequency-specific:

```text
delta-theta 0.5-8 Hz
    hippocampus -> parietal cortex > reverse
    during both encoding and recall

beta 12-30 Hz
    parietal cortex -> hippocampus > reverse
    during both encoding and recall
```

This is an unusually useful calibration target because it predicts a **direction sign flip across frequency bands** rather than merely nonzero connectivity.

The present analysis does not claim to reproduce their complete mixed-effects/group pipeline. It asks whether one clean subject/pair behaves qualitatively consistently with that published group pattern.

---

## 2. Public dataset and anatomically clean pair

Dataset:

```text
OpenNeuro ds004789
UPENN-RAM delayed free recall (FR1)
subject R1022J
session 0
```

The metadata-only sidecar screen found a particularly clean same-hemisphere pair.

### Hippocampus

Bipolar channel:

```text
LB2-LB3
```

Underlying contacts:

```text
LB2  Left dentate gyrus (DG)
LB3  Left CA1
```

### Parietal cortex

Bipolar channel:

```text
LH11-LH12
```

Both underlying contacts are labeled left angular gyrus.

This matters because the first calibration does not depend on a loose `temporal-looking contact` versus `parietal-looking contact` choice. The bipolar pairs are anatomically interpretable from the released electrode sidecars.

Recording:

```text
bipolar EDF size  ~523.8 MiB
sampling rate     1000 Hz
samples/channel   2,951,000
```

The GitHub runner downloaded the public EDF directly from OpenNeuro's S3 storage and completed the analysis without manual data handling.

---

## 3. Epoch construction

The event sidecar contains:

```text
300 WORD events
122 REC_WORD events
805 total annotated events
```

Following the published verbal free-recall analysis as closely as practical:

### Successful encoding

Use the 1.6 s interval immediately after presentation of each `WORD` that was later recalled.

Result:

```text
80 successful-encoding epochs
```

### Recall

Use the 1.6 s interval immediately preceding each `REC_WORD` vocalization, excluding overlapping recall windows.

Result:

```text
85 non-overlapping recall epochs
```

---

## 4. PTE implementation sanity check

Before touching the human recording, `experiments/fr1_pte_calibration.py` runs a synthetic known-direction check.

A source oscillator drives a delayed/noisy target.

Result:

```text
PTE source -> target   0.66768 bits
PTE target -> source   0.12251 bits
forward - reverse     +0.54517 bits
```

So the implementation detects the known synthetic direction before the biological data are analyzed.

This is only an implementation sanity check, not full validation against every detail of the original MATLAB PTE code.

---

## 5. Delta-theta result: 0.5-8 Hz

Directional index is defined here as

```text
DI = (PTE_HIPP->PAR - PTE_PAR->HIPP)
     / (PTE_HIPP->PAR + PTE_PAR->HIPP)
```

so positive means hippocampus -> parietal.

### Successful encoding

```text
trials                     80
HIPP -> angular PTE        1.41674 bits
angular -> HIPP PTE        1.33683 bits
DI                         +0.02902
paired-trial DI mean       +0.02986
paired-trial DI SD          0.09020
median prediction delay    200 ms
median phase bins           13
```

This has the **published group-level sign**:

```text
hippocampus -> parietal
```

### Recall

```text
trials                     85
HIPP -> angular PTE        1.40493 bits
angular -> HIPP PTE        1.25510 bits
DI                         +0.05633
paired-trial DI mean       +0.05631
paired-trial DI SD          0.09174
median prediction delay    213 ms
median phase bins           13
```

Again the sign is:

```text
hippocampus -> parietal
```

So delta-theta matches the published qualitative direction during both task periods.

---

## 6. Beta result: 12-30 Hz

Here negative DI means parietal -> hippocampus.

### Successful encoding

```text
trials                     80
HIPP -> angular PTE        0.90429 bits
angular -> HIPP PTE        0.91468 bits
DI                         -0.00571
paired-trial DI mean       -0.00668
paired-trial DI SD          0.06996
median prediction delay     28.5 ms
median phase bins            12
```

The sign reverses relative to delta-theta:

```text
parietal -> hippocampus
```

### Recall

```text
trials                     85
HIPP -> angular PTE        0.89203 bits
angular -> HIPP PTE        0.90145 bits
DI                         -0.00525
paired-trial DI mean       -0.00511
paired-trial DI SD          0.08106
median prediction delay     28 ms
median phase bins            12
```

Again:

```text
parietal -> hippocampus
```

The beta asymmetry is **small** in this pair. Its usefulness here is primarily the sign reversal, not the magnitude.

---

## 7. Qualitative sign gate

Predictions copied from the published group result before reading the one-subject result:

```text
[1] delta-theta encoding : HIPP -> parietal
[2] delta-theta recall   : HIPP -> parietal
[3] beta encoding        : parietal -> HIPP
[4] beta recall          : parietal -> HIPP
```

Observed:

```text
[1] TRUE
[2] TRUE
[3] TRUE
[4] TRUE
```

So the first real-data calibration matched:

```text
4 / 4 directional signs
```

This is encouraging because the target is not simply `some connectivity exists`; it is a complementary frequency-specific direction pattern.

---

## 8. Surrogate result -- useful but currently too optimistic to headline

The first script also used independently time-shuffled phase surrogates, following the verbal surrogate description in the paper.

With only 60 surrogate draws, all four observed aggregate directional indices exceeded the two-sided surrogate magnitude distribution at the minimum attainable empirical value:

```text
p = 1 / 61 ~= 0.0164
```

Do **not** interpret that as four strong one-subject biological significance results.

The aggregate surrogate distribution is extremely narrow because each surrogate value averages many trial PTEs. That can make the resulting z-scores look implausibly large, especially for the very small beta asymmetry.

Before using inferential language we should add at least:

```text
paired trial-level sign-flip / permutation test
bootstrap confidence interval on trial-wise direction
sensitivity to bin/tau choices
independent direction-sensitive control metric
multi-subject replication
```

The current claim is deliberately only the qualitative sign calibration.

---

## 9. Important implementation choice: Scott expression

The Das & Menon methods text describes a Scott-rule expression of the form

```text
3.49 * phase_SD * M^(-1/3)
```

using wording that can be read as `number of bins`.

Dimensionally and in standard Scott-rule form, that expression is a **bin width**, not an integer bin count. Other published PTE descriptions also use it as a bin size.

The present script therefore uses:

```text
phase_bin_width = 3.49 * average_phase_SD * M^(-1/3)
phase_bins      = ceil(2*pi / phase_bin_width)
```

and records that choice explicitly.

This should be checked against the original Hillebrand/Fraschini implementation before calling any multi-subject number a formal replication.

---

## 10. What this does and does not earn

### It earns

A real-data pipeline now works end to end:

```text
OpenNeuro public FR1
    -> anatomical BIDS selection
    -> exact bipolar hippocampus/parietal pairs
    -> GitHub Actions EDF download
    -> trial construction
    -> phase filtering / Hilbert phase
    -> PTE directionality
    -> known published qualitative frequency signature
```

And one exceptionally clean subject/pair hits all four qualitative signs.

That is enough reason to scale the calibration to several independently selected subjects.

### It does not earn

It does **not** establish:

```text
new hippocampal-parietal connectivity
replication of the 96-subject study
causal physical transmission direction
travelling waves as the carrier
PresentMoment's accessibility-operator hypothesis
a neural mechanism of subjective present duration
```

The PTE result is directed statistical dependence. `FRONTIER_MECHANISM_IDENTIFIABILITY.md` remains the guardrail: effective direction/frontier does not identify microscopic carrier.

---

## 11. Next gate

Do **not** condition connectivity on slow-wave/body state yet.

First expand the calibration automatically across subjects with anatomically strict bipolar selection.

A useful selection rule is:

```text
hippocampal bipolar pair
    both contacts anatomically hippocampal / CA / DG / subiculum

parietal bipolar pair
    both contacts inside angular gyrus, supramarginal gyrus,
    posterior cingulate or precuneus
```

Then ask:

```text
How often do the four qualitative signs replicate across clean subject/pair choices?
```

If the answer is poor, debug the method/selection before opening the new hypothesis.

If the answer is reasonably stable, then the next genuinely new question can be:

> **Does a slow cortical/wave state systematically reweight the fast frequency-specific hippocampus <-> parietal accessibility matrix?**

That is where `TEMPORAL_ACCESSIBILITY_OPERATOR.md` becomes an experiment rather than a synthesis.

---

## Reproducibility

Code:

```text
experiments/fr1_pte_calibration.py
```

GitHub workflow:

```text
.github/workflows/fr1-pte-calibration.yml
```

First real-data workflow run:

```text
31591564632
```

Selected artifact:

```text
fr1-pte-r1022j
```

The raw ~524 MiB EDF is not committed to the repository; it is fetched from the public OpenNeuro dataset during the workflow.
