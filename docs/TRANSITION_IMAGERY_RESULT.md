# Transition imagery gate — held-out result

## Verdict

```text
NO_CLEAN_TRANSITION_ADVANTAGE
```

This result is preserved as a null.  The preregistration is in
`docs/TRANSITION_IMAGERY_GATE.md`; the implementation is
`experiments/sitstand_transition_imagery.py`.

No analysis parameter was changed after opening the exploration set, and the held-out
workflow used the frozen 16 participants S08-S23.

## Question

Does imagined body-state **transition** have a posture-general sensorimotor EEG
signature relative to imagined **state preservation**, after the target/cue mapping is
reversed across train and test posture?

The cross-posture design was:

```text
train while sitting:
    transition = imagine sit -> stand
    static     = imagine sit -> sit

test while standing:
    transition = imagine stand -> sit
    static     = imagine stand -> stand

and reverse.
```

Because target identity reverses its class across posture, a fixed `sit`/`stand` or
up/down-cue decoder cannot explain successful positive transfer.

## Frozen held-out result

```text
n subjects                              16
sensorimotor cross-posture accuracy     0.511156
occipital cross-posture accuracy        0.509542
sensorimotor - occipital                0.001614
bootstrap 95% CI of paired difference  [-0.031362, 0.031804]
sign-flip p (two-sided)                 0.922902
subjects with positive difference       9 / 16
```

The preregistered positive gate required all of:

1. sensorimotor mean > 0.55;
2. paired difference > 0.03;
3. bootstrap CI entirely > 0;
4. sign-flip p < 0.05.

None of the useful effect-size requirements were met.

## Exploration set

The six exploration subjects already pointed the same way:

```text
sensorimotor mean                       0.509627
occipital mean                          0.529986
paired difference                      -0.020360
bootstrap 95% CI                       [-0.098265, 0.054749]
sign-flip p                             0.657087
```

The held-out result therefore did not depend on an unlucky exploratory split.

## Interpretation

This assay does **not** support the claim that simple mu/beta sensorimotor features
contain a robust posture-general code for `imagined transition` versus `imagined state
preservation`.

It does not show that motor imagery lacks internal dynamics, and it does not refute the
mental-abacus observation.  It says the particular proposed bridge from that observation
to a scalp-EEG transition code failed under a cue-reversing, posture-crossed control.

The earlier EEGMMIDB execution<->imagery transfer assay also failed its
sensorimotor-vs-occipital control.  Together the two nulls are a reason to stop treating
broad scalp motor-imagery similarity as direct evidence for `virtual machinery`.

## Stop rule

Do **not** run the raw-EMG gate as a rescue of this failed EEG result.  The EMG question
was conditional on a surviving neural transition signal.  Raw EMG remains useful for a
future independently motivated execution/imagery experiment, but it does not repair
this gate.

## What survives conceptually

The modest surviving statement is behavioral/architectural rather than a result from
this EEG assay:

> learned systems can produce useful behavior in the absence of the external object or
> overt action that originally scaffolded learning.

The mechanism still has to be earned independently.
