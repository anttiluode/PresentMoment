# Transition imagery gate — preregistration

## Status

Frozen before inspecting any transition-vs-static imagery result.

This gate follows the null result in `VIRTUAL_MACHINERY_EEGMMIDB_RESULT.md`.
The EEGMMIDB left/right execution↔imagery assay failed its sensorimotor-vs-occipital
control, so this experiment changes the *question*, not merely the classifier.

The target is now a state-transition property that is unusually well controlled in a
2026 public sit/stand motor-imagery dataset.

Primary dataset:

> Leelakittisin et al., *EEG-Based Dataset Explicitly Targets the Transitions between
> Sitting and Standing for Exploring Neural Activation Patterns in Motor Imagery and
> Execution*, GigaScience (2026), DOI `10.1093/gigascience/giag065`.

Usable participants: 22 (S01-S04, S06-S23; S05 excluded by the dataset authors).

---

## 1. The contrast

The imagery protocol contains four active imagination conditions:

```text
current posture: sitting
    MI_SIT_STD  (trigger 21): imagine standing up      -> TRANSITION
    MI_SIT_SIT  (trigger 22): imagine remaining seated -> STATIC

current posture: standing
    MI_STD_STD  (trigger 31): imagine remaining standing -> STATIC
    MI_STD_SIT  (trigger 32): imagine sitting down       -> TRANSITION
```

The useful design property is:

```text
transition = up cue while sitting + down cue while standing
static     = down cue while sitting + up cue while standing
```

Therefore, when the two postures are pooled:

- arrow direction is balanced across `transition` and `static`;
- starting posture is balanced across `transition` and `static`;
- both classes require active motor imagery rather than comparing imagery with passive
  rest.

This is much harder to dismiss as a simple visual cue or task-engagement effect than
the previous EEGMMIDB left/right assay.

---

## 2. Question

> **Does imagined state change have a neural signature distinguishable from imagined
> state preservation, after balancing cue direction and current posture?**

This is a modest operational contact with the `virtual machinery` idea.

A positive result would mean that the current brain state contains information about
whether the person is internally running a transition away from the current body state
rather than preserving it.

It would NOT establish:

- a literal internal body simulation;
- consciousness;
- free will;
- a unique neural implementation;
- motor execution↔imagery equivalence.

---

## 3. Frozen exploratory/held-out split

To avoid tuning a story into existence:

```text
EXPLORATION / INSTRUMENT SET
    S01, S02, S03, S04, S06, S07

HELD-OUT GATE
    S08-S23 (excluding no additional subjects unless data are missing/corrupt)
```

The exploration set may be used only to verify event parsing, feature scale, and that
the classifier runs.

The following are frozen before held-out evaluation:

- epoch window;
- preprocessing family;
- channel groups;
- feature definition;
- classifier;
- primary comparison;
- verdict rule.

If implementation details must change because the released files differ from the paper,
document the change before opening held-out results.

---

## 4. Frozen primary assay

### Data

Use the authors' processed MI FIF files **if and only if** they retain all four active
imagery conditions (21, 22, 31, 32).

If static conditions were dropped from those files, use the raw synchronized EEG/EMG
release and recreate a common preprocessing pipeline; do not substitute a different
contrast.

### Epoch window

Use `0.5 s to 3.0 s` after imagery cue onset.

Rationale:

- skip the strongest initial visual transient;
- remain within the instructed imagery period;
- use the same clock window for all four conditions.

If the released processed epochs are time-locked differently, stop and document before
changing this.

### EEG groups

Primary sensorimotor set:

```text
FCz, FC1, FC2, FC3, FC4,
Cz, C1, C2, C3, C4,
CPz, CP1, CP2, CP3, CP4
```

Occipital control:

```text
POz, PO3, PO4, PO7, PO8, O1, Oz, O2
```

Use only channels actually present; require at least 5 sensorimotor and 4 occipital.

### Features

Per epoch and channel:

```text
relative log power 8-13 Hz
relative log power 13-30 Hz
normalizing power 4-40 Hz
```

This deliberately reuses the simple feature family from the failed EEGMMIDB assay.
The goal is not to optimize a BCI.

### Classifier

StandardScaler + logistic regression (`C=1`, liblinear, fixed random seed).

### Validation within each subject

The critical leakage problem is posture/cue pairing.

For each participant, evaluate **cross-posture generalization**:

```text
train on sitting trials:
    transition = MI_SIT_STD (21)
    static     = MI_SIT_SIT (22)

test on standing trials:
    transition = MI_STD_SIT (32)
    static     = MI_STD_STD (31)

and reverse:

train on standing
    -> test on sitting
```

Average the two balanced accuracies.

This is stronger than randomly mixing all four conditions because the physical starting
posture and the mapping from cue direction to label both reverse across train/test.

A classifier cannot succeed by learning simply:

```text
up arrow = transition
```

because in the opposite posture the arrow-label relationship reverses.

### Primary subject-level effect

```text
D_subject = accuracy_sensorimotor - accuracy_occipital
```

### Group inference

On the held-out participants:

- report both group accuracies;
- report paired `D_subject`;
- bootstrap 95% CI of mean `D`;
- two-sided sign-flip permutation test;
- report count of subjects with `D > 0`.

### Gate

Call only:

```text
SENSORIMOTOR_TRANSITION_ADVANTAGE
```

if ALL are true on held-out subjects:

1. mean sensorimotor cross-posture balanced accuracy > 0.55;
2. mean `D > 0.03`;
3. bootstrap 95% CI for mean `D` is entirely > 0;
4. two-sided sign-flip `p < 0.05`.

Otherwise:

```text
NO_CLEAN_TRANSITION_ADVANTAGE
```

This threshold is intentionally stricter than merely decoding above chance.

---

## 5. Secondary but important: execution-derived geometry

Do NOT use this to rescue a failed primary gate.

After the primary held-out result is frozen, a second experiment may ask whether an
execution-derived transition signature transfers to motor imagery.

This requires a common raw-data preprocessing/alignment scheme because the dataset's
released ME and MI processed FIFs use different filtering/time-lock conventions.

The clean version should compare:

```text
ME: actual transition vs posture-matched rest
MI: imagined transition vs imagined static
```

and should balance movement direction/posture.

Any cross-domain model must be evaluated against occipital and cue/timing controls.

---

## 6. Output-null / output-suppressed criterion using raw EMG

The raw public release has now been independently inspected from S01 via byte-range
reads.  Each session contains:

```text
eeg          63 x time
eeg_ts       1 x time
emg           6 x time
emg_ts        1 x time
eeg_channels
emg_channels
eeg_fs       1200 Hz
emg_fs       2000 Hz
trigger_labels
```

S01 channel metadata names the six EMG channels:

```text
sl_l, sl_r   soleus
 ta_l, ta_r  tibialis anterior
 rf_l, rf_r  rectus femoris
```

The trigger table explicitly contains 21/22/31/32, including both static-imagery
conditions.

A later stronger gate should quantify EMG during imagery rather than assume instruction
compliance.

A useful criterion is not `EMG == 0` — motor imagery can modulate corticospinal
excitability without overt movement.

Instead ask whether:

```text
execution-like EEG transition structure is present
             while
EMG remains far below execution and lacks an execution-like movement burst
```

If imagery produces execution-scale EMG, the `output-suppressed virtual machinery`
interpretation fails for those trials/participants.

---

## 7. Why this is about the abacus intuition

The mental-abacus story is not simply:

> imagined action resembles real action.

A more useful abstraction is:

> **the organism can internally traverse a learned state transition while the external
> object/body transition does not occur.**

The sit/stand dataset gives a primitive version with the body itself:

```text
current physical body state = sitting
internal requested future   = standing
actual physical body state  = still sitting
```

The static control asks the same person to imagine preserving the current state.

If those two internal trajectories are distinguishable under the cross-posture/cue
controls above, the phrase `internally run transition` gains empirical content.

If they are not, narrow again.

---

## 8. Relation to the subject/control question

Even a positive result would address only the tractable half:

```text
How can a current system invoke a counterfactual trajectory through learned machinery?
```

It does not answer:

```text
Why is any of that trajectory experienced by a subject?
```

Keep that boundary intact.
