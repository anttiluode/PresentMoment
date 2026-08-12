# Causal-age surfaces: a sharper criterion for a thick present

Date: 2026-08-12

This note records the main thing that survived the PerceptionLab living-field / wave-field
experiments.

It is a criterion, not a new architecture and not a claim about consciousness.

---

## 1. Statefulness is too weak

A system can have persistent state and still be temporally boring.

The first-order Living Checkerboard experiment had a persistent spatial field and
multiple read/write compartments, but after a perturbation its channels collapsed toward
a common mode with essentially zero propagation lag.

So:

```text
persistent state != temporal thickness
```

A better question is:

> **How many distinguishable causal ages are simultaneously active and observable in the
> current state?**

---

## 2. The positive construction

PerceptionLab's second-order Wave Field gives each point both a field value and a
velocity:

```text
F_dotdot = c^2 grad^2 F - gamma F_dot + drive
```

A local impulse propagates past spatially separated read apertures.

In the checked run, the field predicted an adjacent-aperture lag of about 13.2 frames.
The Temporal Multi Scope reports mean absolute lag over all probe pairs. With probes
0,1,2,3, the mean pair separation is `10/6` gaps, so the expected mean pairwise lag is:

```text
13.2 * 10/6 = 22.0 frames
```

Manual runs gave approximately:

```text
21.3
21.5
22.2 frames
```

The arithmetic agreement is a calibration of the toy and its instrument, not a fact
about biology.

What it demonstrates is the construction itself:

> **At one wall-clock instant, one spatial state can contain the same event at several
> unfinished propagation stages.**

Call such a state a **causal-age surface**.

---

## 3. Thin clock time, thick causal age

The earlier `THICK_NOW.md` formulation said that an instantaneous whole-organism state
can contain filtered residues of the past.

The wave-field result adds a distinct mechanism:

```text
ringdown / decay:
    the event survives because a variable has not relaxed yet

propagation:
    the event survives because its consequence is still travelling
```

Both can coexist.

A useful schematic state is therefore not only

```text
X(t) = [slow variables with different decay constants]
```

but also

```text
X(t) = [signals at different positions / loop stages / phases]
```

The present can be thin in clock time while containing a spread of causal ages.

---

## 4. Source-specific temporal kernels

The old leaky-bank picture treats temporal channels as anonymous filters:

```text
b_i(t) = integral K_i(tau) u(t-tau) d tau
```

A more physical formulation attaches the kernel to a source or loop:

```text
X(t) = sum_s integral K_s(tau) u_s(t-tau) d tau
```

where `s` may identify a recurrent process, sensorimotor loop, oscillator, organ-scale
process, or any other physically distinct source.

This matters because two channels can differ in more than decay rate:

```text
latency
propagation path
kernel shape
frequency
phase
nonlinearity
receiver
feedback gain
```

So a temporal basis need not be a bag of anonymous clocks. It can be a set of
**source-tagged impulse responses**.

---

## 5. Phase can carry source identity as well as time

A periodic source adds information that a pure decay channel does not have by itself.

For example, a source may contribute approximately

```text
x_s(t) = A_s(t) cos(phi_s(t))
```

If several periodic sources occupy distinguishable frequency/phase structure, a receiver
can in principle separate them by phase-sensitive or frequency-selective readout.

That gives two different coordinates:

```text
amplitude / envelope -> how strongly the source is currently expressed
phase                -> where the source is in its recurrent cycle
```

This does **not** mean periodic channels are universally superior to exponential memory.
It means source identity can be encoded orthogonally to age/strength, rather than asking
one bank of anonymous decay rates to do every job.

This is the clean computational part of the heart/breath intuition: recurring sources
can act as repeated probes whose phase and evoked consequences jointly structure current
state.

Whether real physiology exploits this for temporal cognition is a neuroscience question,
not established by the toy.

---

## 6. Feedback can make travel time part of the oscillator

The PerceptionLab workflow `wave_field_one_home.json` closes a loop of the form:

```text
field read at a distant aperture
    -> controller
    -> write near an earlier aperture
    -> propagation through field
    -> distant read again
```

The propagation path itself contributes roughly three aperture-gap delays before the
controller's own dynamics are counted.

That creates a useful distinction:

```text
explicit timer:
    period is a parameter inside the controller

travel-time loop:
    period can emerge partly from the time required for consequences to return
```

This is the smallest toy version of the broader `brain -> body/world -> brain` idea.

Again: delayed feedback oscillators are not novel. The value here is that the mechanism
is visible and measurable inside the same PerceptionLab instrument used for the negative
control.

---

## 7. Revised working definition

The current working definition of temporal thickness should therefore be:

> **Temporal thickness is the diversity of distinguishable causal ages, phases and
> unfinished loop stages that are simultaneously present, observable and capable of
> affecting what happens next.**

This is stronger than persistence and weaker than a claim about subjective duration.

It naturally includes:

```text
fading residues
signals in flight
cyclic phases
feedback returns
slow chemical/mechanical state
prospective controller state
```

but does not assume that every such variable is conscious or useful.

---

## 8. The measurement requirement

A candidate `wide present` mechanism should not count merely because it has memory.
At minimum ask whether current observations distinguish different causal ages.

Useful tests include:

```text
known perturbation -> measured lag profile
speed/distance change -> predicted lag change
single common mode -> negative control
multiple decay/phase/propagation channels -> identifiability test
receiver ablation -> which temporal distinctions remain observable?
```

PerceptionLab now supplies a simple known-answer calibration case for the first three.

---

## 9. Stop condition

This note is intentionally the end of the current PresentMoment build branch.

The repo does not need another speculative node merely to illustrate the same idea.
The useful outputs are now:

1. the `statefulness != temporal thickness` criterion;
2. the causal-age-surface construction;
3. the source-specific kernel formulation `K_s(tau)`;
4. the distinction between decay, propagation and phase;
5. a public PerceptionLab calibration workflow that anyone can rerun.

Further work belongs where a concrete system can earn something from these distinctions.
