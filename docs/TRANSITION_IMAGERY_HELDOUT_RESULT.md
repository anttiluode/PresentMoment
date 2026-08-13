# Transition imagery gate — held-out result

## Verdict

**NO_CLEAN_TRANSITION_ADVANTAGE**

This is a frozen confirmatory null for the assay specified in
`docs/TRANSITION_IMAGERY_GATE.md`.

Do not tune bands, time windows, channel sets or classifier on these held-out subjects
and present a selected variant as confirmation.

---

## Frozen held-out set

```text
S08 S09 S10 S11 S12 S13 S14 S15
S16 S17 S18 S19 S20 S21 S22 S23
```

`S01 S02 S03 S04 S06 S07` were used only as the exploration/instrument set.
`S05` is excluded in the source dataset.

Dataset:

> Uengsawapak et al., GigaScience 2026, DOI `10.1093/gigascience/giag065`

The test classified imagined **state transition** versus imagined **state preservation**
while forcing generalization across physical starting posture:

```text
train sitting:
    mi_sit_std = transition
    mi_sit_sit = static

test standing:
    mi_std_sit = transition
    mi_std_std = static

and reverse
```

Because arrow direction reverses its label across posture, a fixed up/down visual-cue
rule cannot solve the cross-posture test.

Frozen features:

```text
0.5–3.0 s after imagery cue
relative 8–13 Hz and 13–30 Hz log power
normalized by 4–40 Hz power
StandardScaler + logistic regression
```

Primary comparison:

```text
sensorimotor FC/C/CP electrode set
        versus
occipital PO/O control set
```

---

## Result

### Sensorimotor

```text
mean cross-posture balanced accuracy    0.511156
median                                  0.534375
bootstrap 95% CI                       [0.479272, 0.541978]
subjects > 0.5                          9 / 16
```

### Occipital control

```text
mean cross-posture balanced accuracy    0.509542
median                                  0.517536
bootstrap 95% CI                       [0.479061, 0.539669]
subjects > 0.5                          9 / 16
```

### Primary paired effect

```text
sensorimotor - occipital                +0.001614
bootstrap 95% CI                       [-0.031362, +0.031804]
two-sided sign-flip p                   0.922902
subjects with positive difference       9 / 16
```

Frozen gate required all of:

```text
sensorimotor mean > 0.55                  FAIL
mean SM-occipital > 0.03                  FAIL
95% CI of SM-occipital entirely > 0       FAIL
sign-flip p < 0.05                        FAIL
```

The verdict is therefore unambiguous.

Workflow run: `31686465430`.
Artifact: `9175730353`.

---

## Per-subject scores

```text
       sensorimotor   occipital
S08       0.3958       0.5660
S09       0.5856       0.5234
S10       0.4563       0.4750
S11       0.5375       0.5313
S12       0.4191       0.4521
S13       0.5438       0.5250
S14       0.4221       0.3938
S15       0.4875       0.4875
S16       0.5469       0.6229
S17       0.5313       0.5875
S18       0.5556       0.5115
S19       0.5875       0.5563
S20       0.5661       0.5792
S21       0.6094       0.4833
S22       0.4808       0.4183
S23       0.4531       0.4396
```

---

## What died

The frozen low-dimensional scalp-bandpower hypothesis:

> imagined transition away from the current posture should create a sufficiently stable
> sensorimotor mu/beta signature that generalizes across starting posture and exceeds
> an occipital control.

It did not.

This matters because the design already removed a major easy cue explanation.  The
result is not a near miss:

```text
sensorimotor       ~ 0.511
occipital          ~ 0.510
paired difference  ~ 0.002
```

The simple feature geometry is essentially at chance at the group level.

---

## What did NOT die

This null does not contradict established evidence that motor imagery recruits parts of
motor/premotor/parietal systems, alters corticospinal excitability, or can be decoded in
better tailored BCI paradigms.

Nor does it contradict the mental-abacus lesion case.

It says something narrower and methodologically useful:

> **the particular `transition vs state-preservation` property we wanted is not exposed
> as a robust cross-posture sensorimotor mu/beta bandpower code by this assay.**

The virtual-machinery story therefore does not get to cite this dataset as positive
support.

---

## Combined with the first EEGMMIDB null

We now have two independent failed easy assays:

### EEGMMIDB

```text
question:
    does execution <-> imagery left/right geometry transfer more over sensorimotor
    electrodes than occipital controls?

result:
    SM transfer       0.53607
    occipital         0.53534
    difference       +0.00073
    sign-flip p       0.973
```

### Sit/stand transition imagery

```text
question:
    does imagined transition vs static-state preservation generalize across posture
    more over sensorimotor electrodes than occipital controls?

result:
    SM accuracy       0.51116
    occipital         0.50954
    difference       +0.00161
    sign-flip p       0.923
```

Both point estimates of the critical regional advantage are effectively zero.

That is a much stronger methodological message than one isolated failed classifier.

---

## Next move

Do **not** immediately optimize another EEG classifier on these same labels.

The stronger surviving evidence for `virtual machinery` currently comes from:

```text
causal/selective lesion dissociations
learning trajectories
behavioral timing/error structure
forward-model/efference-copy experiments
```

The raw sit/stand release remains useful for a different question because it contains
synchronized EEG and six-channel EMG.  A future **output-suppression** analysis can ask
whether motor-imagery trials produce covert/subthreshold motor-system effects without an
execution-like EMG burst.

But that should be specified as a new gate, not used to rescue this one.

---

## Current methodological conclusion

The abacus intuition survives as a hypothesis generator.

The easy scalp-EEG signatures did not.

That is exactly the separation this repo needs to preserve.
