# Order sensitivity, not order

Date: 2026-08-12

Several branches of this project have recently made sequence/order look important:

- state-dependent causal-frontier direction;
- active re-entry where the same inverse operations work in one order and fail in the
  other;
- memory/planning literature built around ordered internal sequences.

It would be easy to conclude:

> order keeps reappearing, therefore order itself is the fundamental temporal variable.

That conclusion is too strong.

KYY already provides a direct counterexample.

---

## 1. KYY killed generic temporal order

`KYY/docs/FRONTIER_DIRECTION_GATE.md` compared matched maturity mixtures.

For the phase-only condition:

```text
monotone contiguous blocks      0.9671
non-monotone contiguous blocks  0.9677
coordinate-shuffled             0.9450
```

The small residual advantage survived when contiguous phase blocks were placed in a
non-monotone order. The effect therefore belonged to spatial contiguity/coherence, not
temporal order.

When genuinely immature pre-state was included, monotone ordering was slightly worse.

So the cross-repo rule must remain:

> **There is no generic computational virtue in putting states into temporal order.**

Any new order claim needs a mechanism that makes swapping operations consequential.

---

## 2. The sharper variable: order sensitivity

The active-reentry toy uses two state transitions `A` and `B`.

Encoding applies:

```text
A then B
```

and a correct re-entry must undo them in reverse.

The interesting property is not that a sequence exists. It is that:

```text
AB != BA
```

so the same constituents composed in different orders reach different states.

That suggests a better counterfactual definition:

> **A system is order-sensitive for a receiver/task when a permutation of matched
> constituent transitions changes future accessibility or control-relevant output.**

This includes noncommuting linear operators as the simplest example, but the definition
is broader. Order sensitivity can arise from nonlinear saturation, state-dependent gain,
plasticity, irreversible updates, causal dependencies, depletion/recovery, or any other
path dependence.

If matched permutations produce the same reachable/readable state, order is ornamental
for that question.

---

## 3. New known-answer gate

The implementation is:

```text
experiments/reentry_order_sensitivity.py
```

It sweeps 100 pairs of 3-D rotations:

```text
A = Rz(a)
B = Rx(b)
a,b in 0..90 degrees
```

For each pair it computes:

```text
commutator magnitude
    ||AB - BA||_F

wrong-order signal penalty
    loss of fixed receiver label signal after replaying
    the same inverse actions in the wrong order
```

Local run:

```text
grid points                          100
corr(commutator, order penalty)   +0.951550
max commutator norm                2.449490
max wrong-order penalty            1.000000
```

A commuting control uses two rotations about the same axis:

```text
A = Rz(a)
B = Rz(b)
```

and gives, to numerical precision:

```text
max commutator norm      ~1.6e-16
max order penalty        ~3.3e-16
```

This is constructed mathematics. It does not discover a biological mechanism.

Its purpose is to calibrate the wording:

```text
ORDER EXISTS
    weak / common

ORDER IS DECODABLE
    still weak

ORDER CHANGES THE FUTURE UNDER MATCHED PERMUTATION
    the load-bearing property
```

---

## 4. Procedural addressing should therefore be conditional

The active-reinstatement note proposed that some memories may be recoverable through a
procedure/trajectory rather than a static content key.

That idea should now be stated more carefully.

A useful **procedural address** requires more than repeating a familiar sequence.
It requires that the trajectory changes what becomes accessible.

Schematically:

```text
same starting trace
same action/context ingredients

trajectory pi_1
    -> target becomes receiver-potent

permuted trajectory pi_2
    -> target remains null / different
```

If every permutation gives the same reinstatement after matched time, effort and cues,
then the action sequence was not a meaningful address. At most the ingredients mattered.

This gives the phenomenological claim a proper way to fail.

---

## 5. Current neuroscience makes sequence control plausible, not established

Three recent primary results are relevant but should not be collapsed into one mechanism.

### Action plans align hippocampal internal sequences

Zutshi et al. (Nature, 2025, DOI `10.1038/s41586-024-08397-7`) recorded mice in a task
that separated external cues from changing task relevance. Hippocampal activity was more
strongly aligned with online action plans than with the external variables themselves;
internally generated cell-assembly sequences were selected and updated with goal-directed
action progression.

This says hippocampal sequence content can be organized around action plans. It does not
show deliberate memory re-entry in humans.

### Goal-directed theta sweeps

Tang et al. (Nature Neuroscience, 2026, DOI `10.1038/s41593-026-02364-3`) reported in rats
that learning-dependent hippocampal theta sweeps predicted upcoming goal-directed
trajectories, coordinated with prefrontal activity, and were preferentially replayed
during sharp-wave ripples. The same paper reports context-specific latent maps.

This is particularly relevant to the idea of an internally generated trajectory that
samples/evaluates possible futures. It still does not establish a conscious controller
choosing a neural phase path.

### Human ripple-linked planning sequences

He et al. (Nature Neuroscience, 2026, DOI `10.1038/s41593-026-02291-3`) recorded human
iEEG during LEGO-like inference tasks. Hippocampal-ripple-associated replay reorganized
building blocks into candidate sequences while medial-prefrontal representations were
updated toward inferred solutions.

This is the strongest current human connection to internally assembled candidate
sequences in our thread, but it is planning/inference evidence, not proof that ordinary
forgotten-word retrieval uses the same mechanism.

---

## 6. The experiment should now permute trajectories, not compare power

A strong brain-side test is no longer:

```text
memory success correlates with theta power
```

or:

```text
congruent movement > no movement
```

Those leave too many explanations alive.

The sharper matched design is:

```text
same learned material
same constituent actions/cues
same total duration
same gross movement/effort

A. encoding-congruent trajectory/order
B. same constituents, scrambled order
C. matched unrelated trajectory
D. imagery-only trajectory
E. no re-entry
```

Measure target-specific accessibility over time:

```text
when does target information become decodable?
which receiver gets it first?
how long does it remain potent?
does the correct trajectory alter later behavior?
```

The load-bearing contrast is:

```text
congruent order - matched scrambled order
```

If it is zero after proper controls, the strong procedural-address hypothesis should be
downgraded even if both action conditions beat rest.

---

## 7. Keep brain order separate from software decision-tree order

The WidePresent re-entry card also uses ordered probes, but its current probes are
read-only observations.

There, order matters mainly for **cost**:

```text
cheap routing probe first
    -> avoid irrelevant expensive measurement
```

Reading the same complete set in another order eventually produces the same state
estimate.

That is not noncommuting dynamics.

So there are at least two distinct uses of order:

```text
DIAGNOSTIC ORDER
    same final evidence, different cost to acquire it

DYNAMICAL ORDER
    same constituents, different order changes the reachable/readable state itself
```

Do not conflate them.

---

## 8. Revised PresentMoment object

The earlier object was:

```text
current latent state
+ causal age
+ receiver accessibility
+ available control trajectories
```

Add one conditional property:

```text
path sensitivity of those trajectories
```

A useful descriptive object is therefore not merely a width or an ordered frontier.
It is closer to:

```text
for each receiver:
    what is readable now?
    what actions can change readability?
    which permutations of those actions are equivalent?
    which are not?
```

This makes the "present" partly a structure of **reachable future readouts from the
current state**, not simply a bag of traces from the past.

---

## 9. Sentence to keep

Do not say:

> order is fundamental.

Say:

> **Order becomes a temporal variable only where the system is path-sensitive: the same
> ingredients composed differently lead to different future accessibility or control.**

That sentence is consistent with both the active-reentry positive toy and the KYY order
null.
