# EEGMMIDB virtual-machinery gate — result

## Verdict

**NO_CLEAN_SENSORIMOTOR_ADVANTAGE**

This is a preserved null / narrowing result.

The experiment asked whether left-vs-right movement geometry learned from **executed**
movement transfers to **imagined** movement (and vice versa) more strongly in a
sensorimotor electrode set than in an occipital control set.

The answer in the first frozen 12-subject cohort was essentially **no**.

Do not rescue this result by changing bands, channel sets, classifiers or time windows
on the same 12 subjects and then presenting the best variant as confirmation.

---

## Dataset and frozen assay

Dataset: PhysioNet EEG Motor Movement/Imagery Database v1.0.0, DOI
`10.13026/C28G6P`.

Subjects: `S001`–`S012`.

Runs:

```text
execution: 3, 7, 11   left fist vs right fist
imagery:   4, 8, 12   left fist vs right fist
```

Epoch: 0.5–3.5 s after task annotation.

Features:

```text
relative log bandpower
mu    8–13 Hz
beta 13–30 Hz
normalization band 4–40 Hz
```

Classifier: standardized logistic regression.

Within-condition validation: leave-one-run-out.

Cross-condition tests:

```text
execution -> imagery
imagery   -> execution
```

Primary anti-confound comparison:

```text
sensorimotor FC/C/CP electrodes
             versus
occipital PO/O electrodes
```

The control was necessary because the task structure itself can carry left/right
information across execution and imagery.  Cross-condition decoding alone therefore
cannot be called motor reinstatement.

Implementation: `experiments/eegmmidb_virtual_machinery.py`.

Workflow run: GitHub Actions `31684530833`, artifact `9174868144`.

---

## Result

### Sensorimotor electrodes

```text
within execution          0.62004
95% bootstrap CI          [0.55654, 0.68279]

within imagery            0.57019
95% bootstrap CI          [0.50868, 0.63741]

execution -> imagery      0.53423
95% bootstrap CI          [0.47715, 0.59164]

imagery -> execution      0.53791
95% bootstrap CI          [0.46698, 0.62095]

mean cross-transfer       0.53607
95% bootstrap CI          [0.47577, 0.60062]

left/right contrast cosine
mean                      0.06505
95% bootstrap CI          [-0.16120, 0.28970]
```

### Occipital control electrodes

```text
within execution          0.56696
95% bootstrap CI          [0.51662, 0.61210]

within imagery            0.54960
95% bootstrap CI          [0.49405, 0.60417]

execution -> imagery      0.53474
95% bootstrap CI          [0.49220, 0.57668]

imagery -> execution      0.53595
95% bootstrap CI          [0.50054, 0.56658]

mean cross-transfer       0.53534
95% bootstrap CI          [0.50182, 0.56773]

left/right contrast cosine
mean                      0.18674
95% bootstrap CI          [-0.06923, 0.42106]
```

### Primary paired comparison

```text
sensorimotor transfer     0.536069
occipital transfer        0.535344
---------------------------------
SM - occipital            0.000725
95% bootstrap CI          [-0.057782, 0.058926]
sign-flip p, two-sided    0.97315
subjects with SM > Occ    6 / 12
```

The difference is not merely non-significant.  Its point estimate is approximately
**seven ten-thousandths of balanced-accuracy units**.

The contrast-vector alignment did not rescue the story:

```text
SM - occipital cosine     -0.12168
95% bootstrap CI          [-0.35323, 0.12773]
sign-flip p               0.34278
subjects positive         5 / 12
```

---

## Interpretation

There is some left/right information within both conditions and some apparent
cross-condition information.

But the quantity that mattered was not:

> can a classifier transfer at all?

It was:

> **is that transfer specifically stronger over task-relevant sensorimotor circuitry
> than over a region able to carry shared sensory/task information?**

On this assay, it is not.

Therefore the current data do **not** provide clean evidence that the transfer reflects
reinstatement of a motor-specific internal machine.

A conservative explanation remains sufficient:

```text
shared cue / task / timing structure
       -> information in execution
       -> information in imagery
       -> apparent cross-condition transfer
```

This is precisely why the occipital arm was included.

---

## What this result does NOT say

It does **not** show that motor imagery fails to reuse motor circuitry.

That broader proposition already has independent support from lesion, imaging,
stimulation and motor-imagery literatures.

It says only:

> **this EEGMMIDB feature/decoder/control assay does not isolate that reuse.**

Likewise it says nothing direct about consciousness, subjectivity, the existence of a
self, or the mental-abacus case.

The result kills an instrument, not the whole research question.

---

## Why this null is useful

The mental-abacus intuition tempted a very easy story:

```text
execution and imagery share information
therefore the physical machine is replayed internally
```

This dataset shows why that inference is unsafe.

A representation may cross conditions because the **task** is shared, even when the
feature is not specifically evidence of the machinery we care about.

So future tests need at least one of:

```text
cue-matched controls that remove shared sensory labels
simultaneous EMG proving the ordinary output channel is quiet
causal interference/lesion evidence
transition geometry rather than static condition labels
learning-dependent emergence of the shared geometry
```

This materially sharpens `VIRTUAL_MACHINERY_AND_CONTROL_HANDLES.md`.

---

## Next external gate: output-null motor imagery

A stronger public dataset was published in 2026:

> *EEG-based dataset explicitly targets the transitions between sitting and standing
> for exploring neural activation patterns in motor imagery and execution*
> (GigaScience 15, 2026, `giag065`, DOI `10.1093/gigascience/giag065`).

It contains 22 usable healthy participants with synchronized:

```text
60-channel EEG
EOG
EMG
motor execution
motor imagery
sit -> stand
stand -> sit
```

The important addition is **EMG**.

That enables a much better version of the hypothesis:

```text
execution transition geometry present in EEG
              |
              v
partly recoverable during imagery
              +
execution-like muscular output absent in EMG
```

If that survives proper cue/task controls, the phrase **output-null virtual machinery**
will have earned substantially more content.

If it does not, narrow again.

---

## Method rule carried forward

The next analysis should be specified before inspecting its final held-out subjects.

Do not tune a result into existence.

The point of this branch is to find which parts of the intuitive picture survive
contact with systems we did not build.
