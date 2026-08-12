# State-dependent causal frontiers: direction, phase, and receiver order

Date: 2026-08-12

This note updates the `causal-age surface` picture after the PerceptionLab wave-field
calibration and a pass through recent direct human/animal experiments.

It does **not** reopen the branch as a request for another illustrative node.
The goal is to sharpen what the biological target would have to be.

---

## 1. Correction: objective age is global; maturity is receiver-relative

The phrase `causal age` is useful shorthand, but it can mislead.

At one objective instant `t`, an event that occurred at `t0` has one wall-clock age:

```text
age = t - t0
```

What can differ across locations or populations is which source time has reached a
particular receiver and how far a consequence has progressed through its path.

For a fixed-delay source `s` and receiver `r`:

```text
receiver input:   y_r(t) = u_s(t - d_sr)
frontier:         F_sr(t) = t - d_sr
```

So the more precise object behind the PerceptionLab wave snapshot is a
**retarded-time / receiver-maturity surface**.

This gives a useful bridge to KYY's receiver-relative readout work:

> **meaning can be receiver-relative, and causal maturity can be receiver-relative,
> while objective clock time remains global.**

---

## 2. The PerceptionLab toy used a fixed frontier geometry

The calibrated Wave Field sends a pulse through a fixed spatial medium.

In that construction the order is essentially fixed:

```text
probe 0 -> probe 1 -> probe 2 -> probe 3
```

Changing wave speed or probe spacing changes the lag, but not the basic ordering.

That is enough for a known-answer temporal instrument.

It may be too simple for the biological hypothesis.

---

## 3. Human memory waves suggest that the frontier geometry can reorganize

**Mohan et al. (2024), Nat Human Behaviour, PMID 38459263,
DOI 10.1038/s41562-024-01838-3.**

Using direct human cortical recordings, the authors reported theta/alpha travelling
waves that tended to propagate posterior-to-anterior during successful episodic memory
encoding and anterior-to-posterior during recall.

That is interesting here because it implies that the same anatomy need not impose one
fixed order of phase arrival across cortex.

Schematically:

```text
encoding:
posterior  --->  anterior

recall:
anterior   --->  posterior
```

The relevant quantity is therefore not only

```text
how wide is the frontier?
```

but also

```text
which receivers are early, late, upstream or downstream in the current dynamical mode?
```

---

## 4. The shape can change, not only the direction

**Das et al. (2026), Nature Communications 17:5143,
PMID 41963323, DOI 10.1038/s41467-026-71386-z.**

Direct human recordings during memory tasks revealed planar, rotational/spiral,
concentric source/sink and more complex travelling-wave patterns. Different patterns
and strengths distinguished behavioral states, and some patterns carried information
about individual remembered items.

This makes a one-dimensional `source -> receiver -> receiver` picture even less
adequate.

A current cortical state may have a propagation geometry such as:

```text
plane       one broad ordering
source      one region early -> many outward receivers
sink        many regions -> one convergent receiver
spiral      phase order wraps around a center
complex     several local orderings coexist
```

Again, this does not establish that those patterns are a temporal code.

It says that if propagation contributes to cognition, the causal frontier can have a
**state-dependent shape** rather than merely a fixed width.

---

## 5. A causal intervention says direction is not always epiphenomenal

**Lee et al. (2026), PNAS 123:e2527296123,
PMID 42085148, DOI 10.1073/pnas.2527296123.**

The authors developed travelling-wave transcranial alternating-current stimulation
(twtACS), validated the imposed directional field with human intracranial recordings,
and reported direction-dependent effects on neural timing and human cognitive
performance; monkey recordings also showed directionally shifted spiking.

This is stronger than a correlation between spontaneous wave pattern and behavior.

But the guardrail remains:

```text
causal effect of wave direction on neural timing / behavior
    !=
proof that the brain reads wave position as event age
```

What it earns for PresentMoment is narrower:

> **spatial order and direction of neural timing can itself be a functionally relevant
> variable.**

That makes `frontier geometry` a legitimate analysis target.

---

## 6. Breathing gives a recurrent externally perturbable source

**Mowla et al. (2026), Nature Communications 17:6949,
PMID 42209532, DOI 10.1038/s41467-026-73828-0.**

Human intracranial recordings showed widespread synchronization of forebrain neural
oscillations with breathing. During externally controlled mechanical ventilation, the
imposed breathing rhythm entrained forebrain activity, supporting a causal body-to-brain
component rather than nasal airflow being the only explanation.

This is useful for the source-specific picture because breathing provides:

```text
known recurrent physical source
+ measurable phase
+ multiple afferent routes
+ distributed receivers
+ experimentally manipulable timing
```

A receiver may therefore be characterized not just by a slow envelope but by its
relationship to a recurrent source phase.

---

## 7. The heart really can act as a recurrent state-dependent probe

**Liu et al. (2026), Nature 651:1068-1076,
DOI 10.1038/s41586-025-10010-4.**

In mice, vagal PIEZO2 cardiac mechanoreceptor activity was time-locked to atrial and
ventricular systole on every heartbeat, while response strength depended on circulating
blood volume. Manipulating this pathway altered compensation to posture change and blood
loss.

For the PresentMoment abstraction, the useful structure is:

```text
repeated source event: heartbeat
phase tag: systole / cardiac phase
state-dependent modulation: filling / blood volume
receiver path: vagal afference
closed-loop consequence: cardiovascular compensation
```

That is why `heart as bell` was nearly right, but `heart as recurring endogenous ping`
is more precise.

The same physical event type repeats, while the returned response is modulated by the
current body state.

---

## 8. The new candidate object is not width but a frontier field

A better schematic whole-organism temporal state is now:

```text
Z(t) = {
    for each source s,
    for each receiver r:
        phase / source identity
        propagation or processing frontier
        local gain
        envelope / ringdown
        receiver readout
}
```

or, loosely,

```text
F_sr(t; state) = newest source stage currently available to receiver r
```

where the effective path can depend on the organism's current dynamical state.

The `wide` in wide present would then mean neither:

```text
a literal perceptual frame lasting N seconds
```

nor merely:

```text
a large memory buffer
```

but something closer to:

> **one clock instant intersecting a heterogeneous, state-dependent field of unfinished
> causal processes whose ordering and legibility differ across receivers.**

---

## 9. The important consequence: order may matter more than span

Suppose two states have the same maximum propagation delay:

```text
State A frontier span = 100 ms
State B frontier span = 100 ms
```

but the receiver order differs:

```text
A: visual -> hippocampal -> frontal
B: frontal -> hippocampal -> visual
```

A scalar `present width = 100 ms` would call them identical.

They need not be computationally identical at all.

So future analyses should retain at least:

```text
frontier span
frontier ordering / direction
frontier shape / mode
receiver-specific observability
phase relationships
```

This is a stronger correction than simply adding another timescale.

---

## 10. A concrete brain test, if this branch is ever reopened

Do not build another synthetic field first.

Use an existing intracranial travelling-wave dataset and ask a receiver-relative
question.

For each stable wave epoch:

1. estimate propagation mode/direction;
2. define spatial receiver groups along that mode;
3. estimate when task-relevant information becomes decodable at each receiver;
4. ask whether the order of earliest useful decoding shifts with wave direction/mode;
5. control for local power, electrode distance, common phase, trial difficulty and
   non-wave epochs;
6. phase-shuffle / spatial-shuffle the wave geometry as negative controls.

The key prediction is not merely higher decoding during waves.

It is:

> **if the wave frontier is functionally organizing receiver maturity, reversing or
> changing wave geometry should predictably reorder where useful information becomes
> available first.**

A null result would be important: it would say that visible wave propagation is not the
right bridge from PerceptionLab's causal surface to biological computation.

---

## 11. Guardrail: do not turn phase maps into packets

A cortical travelling wave is not automatically a message packet physically moving from
one electrode to the next.

Similar phase-gradient patterns can arise from interacting oscillators, distributed
inputs, local propagation and other mechanisms. The papers above establish structured
spatiotemporal organization and, in the stimulation case, a causal role for imposed
spatial timing. They do not establish the exact microscopic carrier assumed by the
PerceptionLab wave PDE.

So keep three levels separate:

```text
measured phase / wave geometry
functional receiver timing
microscopic physical transmission mechanism
```

The first is measurable.
The second is testable.
The third must not be guessed from the first two.

---

## 12. Current synthesis

The PerceptionLab accident now contributes a useful negative/positive calibration:

```text
statefulness alone -> not enough
finite propagation -> receiver-relative maturity exists
```

The recent neuroscience adds a harder possibility:

```text
receiver-relative maturity may itself be dynamically reordered
```

So the sentence to carry forward on the brain side is:

> **A biological wide present may be less like a longer frame and more like a
> continuously deforming causal frontier across brain and body.**

That remains a hypothesis.
But it is now specific enough to be wrong.
