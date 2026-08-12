# Temporal accessibility operator: from `present width` to state-dependent causal access

Date: 2026-08-12

This note is a synthesis after the PerceptionLab propagation calibration, the KYY
partial-maturity controls, and a pass through recent human brain work.

It does **not** claim a new mathematical object.  Response kernels, transfer functions,
directed connectivity, communication-through-coherence, phase-dependent routing, and
state-dependent effective connectivity are established ideas.

The proposal here is narrower:

> The most useful measurable target for `PresentMoment` may not be a scalar width at all.
> It may be the **state-dependent pattern of which sources and past lags are currently
> able to influence which receivers.**

That reframing makes several earlier branches fit together without requiring one master
clock, one global travelling packet, or one phenomenological time window.

---

## 1. A scalar causal-width kernel was already too compressed

Earlier notes defined a causal influence kernel schematically as

```text
K_t(Delta) = change in current state/decision when information from t-Delta is removed
```

That asks a useful question: how far backward does current computation remain sensitive?

But it collapses several distinctions that the recent work made unavoidable:

```text
which source?
which receiver?
which frequency / phase channel?
which sign or gain?
which current arousal/body state?
which physical or effective delay path?
```

Two organisms can therefore have the same maximum lag support and still expose very
different information to the computation happening now.

---

## 2. Receiver-resolved response kernel

A more informative analysis object is a state-dependent response operator

```text
K_{r <- s}(t, Delta)
```

or, when frequency/phase matters,

```text
K_{r <- s}(t, Delta, f)
```

with the interpretation

```text
source s at time t-Delta
       |
       |  current-state-dependent pathway
       v
receiver r at time t
```

Locally, one can write a functional derivative

```text
K_{r <- s}(t, Delta)
    = delta y_r(t) / delta u_s(t-Delta)
```

or use whatever empirical directed-connectivity / perturbation measure is appropriate.

This is ordinary systems language.  The important point is what is retained instead of
marginalized away.

A scalar `present width` is then only one summary, for example the largest `Delta` over
which some norm of `K` is appreciable.

---

## 3. Why the PerceptionLab wave calibration still matters

The PerceptionLab Wave Field is a known-mechanism positive control.  A local impulse is
observed at spatially separated probes with the lag predicted by speed and distance.

That fixture establishes an **effective temporal frontier**:

```text
same objective now
+ receiver-specific delays
+ distinguishable unfinished stages
```

But `experiments/frontier_mechanism_aliasing.py` adds an important negative control:

```text
sequential propagation with delays 2,5,9,14
```

and

```text
common broadcast + receiver delays 2,5,9,14
```

produce exactly the same passive receiver traces and pairwise lags.

Therefore:

> **A lag/frontier can be measurable while its microscopic carrier remains
> unidentifiable from passive timing alone.**

This prevents us from reading the known PerceptionLab wave mechanism back into brain
data merely because the brain shows a delay gradient.

---

## 4. The 2026 Yang result looks more like a scheduler than a delay line

Yang, Leopold, Duyn & Liu (Nature Communications 2026,
DOI `10.1038/s41467-026-69068-x`) report human infra-slow fMRI events lasting roughly
10–15 s that progress from sensorimotor toward default-mode regions and are coordinated
with reciprocal changes in visual-semantic encoding and memory retrieval.

The important part for this repo is not simply that there is a slow spatial wave.

Their discussion explicitly raises two hypotheses:

1. the apparent fMRI progression is unlikely to be explained purely by ordinary
   corticocortical axonal conduction because the timescales are mismatched;
2. a subcortical/neuromodulatory process could broadly broadcast to neuronal groups whose
   response composition/delay differs across the cortical hierarchy.

They further hypothesize that the resulting multi-second activation gradient may set the
**dominant direction of information flow occurring on much faster millisecond
Timescales**.  They label that direction-of-flow interpretation as a hypothesis requiring
future tests.

This suggests a two-timescale object:

```text
slow state z(t)
    |
    v
changes effective fast coupling K(t, Delta, f)
    |
    v
fast sensory / mnemonic information flow
```

The slow variable need not itself carry the detailed content.  It can change which
content pathways are currently potent.

---

## 5. Do not replace that with one master direction

Human iEEG gives an important correction.

Das & Menon (Cerebral Cortex 2024, DOI `10.1093/cercor/bhae287`) replicated
frequency-specific directed hippocampal-parietal connectivity across three episodic
memory tasks in a large intracranial cohort.

The broad pattern is not well described as one global arrow that flips wholesale between
encoding and recall.  Directed interactions are frequency-specific; delta/theta and
higher-frequency channels can show different directional asymmetries.

This sits beside Mohan et al. (Nature Human Behaviour 2024,
DOI `10.1038/s41562-024-01838-3`), who found theta/alpha cortical travelling-wave
direction tending posterior-to-anterior during successful encoding and
anterior-to-posterior during recall.

These findings are not contradictions.  They measure different spatial scales,
frequencies and directional objects.

The safer synthesis is:

> **The brain may multiplex simultaneous directed interactions, while cognitive state
> changes their relative potency rather than flipping one master arrow.**

That is exactly why a frequency/receiver-resolved operator is a better analysis target
than one scalar direction or width.

---

## 6. Body cycles belong inside the coupling graph, not beside it

Two 2026 results make the old `bank of independent body clocks` picture particularly
misleading.

### Breathing

Mowla et al. (Nature Communications 2026,
DOI `10.1038/s41467-026-73828-0`) used human intracranial recordings and found widespread
forebrain synchronization to breathing.  Crucially, when breathing was imposed by
external mechanical ventilation under conditions eliminating voluntary respiratory
drive, the imposed rhythm entrained forebrain activity.

That provides a causal body-to-brain source with measurable phase.

### Heart

Liu et al. (Nature 2026, DOI `10.1038/s41586-025-10010-4`) identified vagal PIEZO2
cardiac mechanoreceptors whose activity is heartbeat-coupled and time-locked to systole,
while response strength depends on blood volume.  Manipulating this pathway changes
cardiovascular compensation.

So heartbeats can be recurrent physical probes whose returned afferent signal is modulated
by current body state.

At the same time, a 2026 **bioRxiv preprint** by Jacobsen et al.
(DOI `10.64898/2026.01.06.697926`) reports an infraslow locus-coeruleus/norepinephrine
rhythm that causally modulates heart-rate dynamics during NREM sleep and covaries with
spindle-related memory processing.

Taken together, these examples argue against writing

```text
brain clock + heart clock + breathing clock
```

as independent terms.

A more faithful schematic is recurrent:

```text
brain -> body -> brain
  ^               |
  +---------------+
```

Source and receiver roles can swap around a loop.

---

## 7. A closed-loop formulation

A schematic multivariate system is

```text
x_r(t)
  = u_r(t)
  + sum_s integral K_{r <- s}(t, Delta) x_s(t-Delta) dDelta
```

or in a local frequency-domain approximation

```text
X(omega) = [I - K(omega)]^{-1} U(omega)
```

with the warning that real physiology is nonlinear and nonstationary, so this is an
analysis scaffold, not an assumed generative law.

A recurrent heartbeat, breath, cortical rhythm, endocrine variable or hippocampal event
can therefore be simultaneously:

```text
source of one pathway
receiver of another
state variable changing a third pathway's gain
```

That is richer than attaching an anonymous decay constant to every variable.

---

## 8. The danger / long-moment intuition should be split into separate observables

The original intuition that dangerous moments can seem `longer` remains worth taking
seriously, but `longer` is not one psychological quantity.

Lamprou-Kokolaki et al. (Consciousness and Cognition 2024,
DOI `10.1016/j.concog.2024.103635`) found that increasing naturalistic event density can
make the same interval judged **longer** while also making the **passage of time feel
faster**.

Yue et al. (Psychonomic Bulletin & Review 2026,
DOI `10.3758/s13423-025-02833-z`) found that the number of recalled subevents strongly
predicts retrospective judgments of whole-event duration, including changes in duration
judgment across a one-week delay.

So at least keep separate:

```text
online interval estimate
felt speed / passage of time
retrospective remembered duration
event segmentation density
memory strength / detail
```

This makes a different danger hypothesis plausible:

> **Arousal may change mode occupancy, gain and event segmentation, thereby changing the
> memory structure from which duration is later reconstructed, without literally
> widening a unitary sensory present.**

Yang et al. speculate that high arousal may terminate the normal infra-slow alternation
and bias the system toward sustained outward/sensory encoding.  Connecting that specific
mechanism to subjective danger-time distortion is an inference for future testing, not a
result established by either paper.

---

## 9. What `wide present` means under this reframing

The weak formulation was

```text
present width = N seconds
```

The stronger candidate is

```text
P(t) = {
    K_{r <- s}(t, Delta, f),
    source/receiver phases,
    active ringdowns,
    effective delays/frontiers,
    current gains and readout states
}
```

A present is `thick` when current behavior depends on a heterogeneous structure over
source, receiver and lag—not simply when some variable persists for a long time.

The scientifically interesting quantities become things such as:

```text
lag support
source-receiver sparsity
frequency-specific directionality
phase-dependent gain
loop gain / return time
state-dependent reconfiguration rate
receiver-specific observability
```

No single one is proposed as *the* neural correlate of the present.

---

## 10. A real-data test that would move this beyond synthesis

The next useful experiment should use human intracranial data rather than another
illustrative oscillator.

The public FR1 corpus has now been migrated to OpenNeuro as `ds004789` and contains
hundreds of subjects / recordings.  Mohan et al.'s public travelling-wave code targets
the same RAM/free-recall family.

A staged test is:

### Calibration

1. select subjects with hippocampal plus cortical coverage;
2. reproduce a known frequency-specific directional result with a conservative directed
   metric;
3. verify that electrode labels, referencing and event windows reproduce published
   qualitative structure before asking a new question.

### New question

Condition directed source->receiver coupling on a simultaneously estimated slow or
travelling-wave state.

For example:

```text
Does K_{cortex <- hippocampus}(f, Delta)
change with cortical wave direction / phase?

Does K_{hippocampus <- cortex}(f, Delta)
change reciprocally?
```

The important outcome is not `waves improve memory`.

It is whether a measured slow/spatial state predicts **reconfiguration of the fast
directed accessibility matrix** after controlling for local power, trial type, electrode
distance and common phase.

---

## 11. Falsifiers

This synthesis should be allowed to die.

It loses force if, under adequate controls:

```text
1. receiver-resolved coupling is stationary across the candidate slow/body states;
2. apparent direction changes disappear after power/common-drive controls;
3. wave/frontier phase predicts no reordering or gain change in task-relevant readout;
4. body phase adds no predictive/causal information once ordinary neural state is known;
5. subjective duration effects are fully accounted for by event/memory variables with no
   relation to the proposed state-dependent accessibility changes.
```

A null here would still leave ordinary memory dynamics, travelling waves, interoception
and time perception intact.  It would only kill their proposed synthesis as one object.

---

## 12. Current sentence

The sentence that currently survives best is:

> **A biological `wide present` may be less like a longer frame and more like a
> state-dependent accessibility pattern: which recent sources, phases and bodily/neural
> loops are able to influence which receivers now.**

That is a hypothesis, not a discovery.

Its advantage over `present width` is that it is directly attackable with perturbation,
directed-connectivity and decoding analyses on real data.
