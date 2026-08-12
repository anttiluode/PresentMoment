# Active reinstatement: retrieval as a control-and-observability problem

Date: 2026-08-12

This note starts from a very ordinary phenomenological observation:

> when something is forgotten, one useful strategy is often not to stare harder at the
> missing item, but to re-enact what one was doing, re-enter the sequence, recover the
> rhythm/context, or wait for the thought to come around again.

That observation should not be promoted directly into a claim about hippocampal loops.
But it exposes a missing variable in the current `PresentMoment` framing.

So far the project has mostly asked about **observability / accessibility**:

> which parts of distributed current state are readable by a particular receiver now?

Re-enactment adds the dual question:

> **what can the organism deliberately do to make a currently unreadable trace readable
> again?**

That is a control problem.

---

## 1. Extend the existing ladder

`PUBLIC_AND_PRIVATE_SUBSPACES.md` already separated several claims:

```text
trace exists
    !=
trace is decodable in principle
    !=
trace is legible to this receiver
    !=
trace currently changes behavior
```

Add one more rung between legibility and behavioral control:

```text
trace exists
    !=
trace is readable now
    !=
trace can be MADE readable by an available control trajectory
    !=
trace currently changes behavior
```

A memory can therefore be inaccessible under the current readout without being erased.
The system may have an action, attentional change, imagery routine, contextual cue, or
internal transition that moves the relevant state into a receiver-potent subspace.

This is standard control/observability language, not new mathematics.

---

## 2. Minimal state-space formulation

Let current latent state be `x_k`, current observation be `y_k`, and a selectable control
or state-setting action be `u_k`:

```text
x_{k+1} = A(u_k) x_k + B(u_k) input_k
y_k     = C_k x_k
```

For a fixed control schedule / policy

```text
pi = (u_0, u_1, ... u_T)
```

the important question is not only whether a memory-bearing direction `v` is visible at
`k=0`.

It is whether that direction becomes visible somewhere along the controlled trajectory.
In a linear time-varying approximation this is an observability-Gramian question under a
chosen transition schedule.

Schematically:

```text
v^T W_obs(pi) v
```

can be small for one policy and large for another.

So a useful descriptive object is **policy-relative retrievability**:

```text
R(receiver, memory, now, pi, horizon)
```

rather than a single scalar "memory strength".

---

## 3. The new known-answer gate

`experiments/active_reentry_gate.py` constructs the smallest possible example.

A binary item is initially aligned with the receiver-potent x axis. Two non-commuting
rotations move it into the z axis:

```text
x-axis -- Rz(+90) --> y-axis -- Rx(+90) --> z-axis
```

The fixed receiver only reads `x[0]`, so the item is now present but receiver-null.

With 20,000 noisy trials at the default settings, a local run gave approximately:

```text
static readout            accuracy ~ 0.498
partial re-entry          accuracy ~ 0.498
correct re-entry          accuracy ~ 0.998
same actions, wrong order accuracy ~ 0.503
```

The correct route is:

```text
Rx(-90) -> Rz(-90)
```

The scrambled route uses the **same two inverse actions** in the opposite order.
Because the transition matrices do not commute, the order matters.

This deliberately connects to the earlier switched-system guardrail in
`SILENCE_GAIN_AND_INTERNAL_LOOPS.md`:

```text
[A(state_1), A(state_2)] != 0
```

means the path through state space can matter, not just the amount of time spent in each
state.

Again, the result is constructed. It proves feasibility and checks the code; it is not
evidence that biological recall literally uses rotation matrices.

---

## 4. "Wait for the loop" is a different mechanism

The same experiment also includes an autonomous periodic control.

The item remains in latent state while a slow rotation repeatedly carries that state
through the fixed readout axis.

At the default 15 degree phase step the local known-answer run gives roughly:

```text
phase   0 deg   accuracy ~ 0.50
phase  90 deg   accuracy ~ 0.998
phase 180 deg   accuracy ~ 0.50
phase 360 deg   accuracy ~ 0.50
```

That gives two distinct retrieval primitives:

```text
ACTIVE RE-ENTRY
choose a trajectory that makes the trace readable

PHASE SCAN / WAIT
allow ongoing dynamics to carry the trace through a readable phase
```

They should not be conflated.

A subjective strategy such as "stop forcing it and let it come back" could be consistent
with many mechanisms, including ordinary cue-driven association, reduced interference,
or spontaneous reinstatement. The toy only says that periodic accessibility is a coherent
systems possibility.

---

## 5. Why the current memory literature makes this seam plausible

Several existing results fit the weaker idea that retrieval is a dynamical
reconstruction rather than a static lookup.

### Coordinated reinstatement

Pacheco Estefan et al. (2019, Nature Communications,
DOI 10.1038/s41467-019-09569-0) recorded human hippocampus and lateral temporal cortex.
Hippocampal item-context reinstatement preceded later cortical item reinstatement, and
hippocampal-cortical phase synchronization predicted cortical reinstatement.

Kragel et al. (2021, Nature Communications,
DOI 10.1038/s41467-021-24393-1) found separable reinstatement of temporal context and
semantic content during human episodic recall.

These results support staged / receiver-specific reconstruction. They do not establish
intentional control of a loop.

### Ripple-triggered expansion

Kerrén, Michelmann & Doeller (2026, Nature Communications,
DOI 10.1038/s41467-026-75345-6) report that successful human retrieval is followed by a
hippocampal-ripple-locked expansion of cortical representational dimensionality, with
hippocampal-theta / cortical-gamma coupling preceding the expansion.

The processed-output audit already recorded in this repo found that the reported
post-ripple dimensionality interaction survives the simplest static trial-count
imbalance check.

The conservative relevance here is:

> **readability itself can unfold after an endogenous event.**

### Replay can assemble candidate sequences

He et al. (2026, Nature Neuroscience,
DOI 10.1038/s41593-026-02291-3) recorded 28 human iEEG participants performing
LEGO-like inference tasks. Hippocampal ripples were associated with replay that assembled
building blocks into candidate sequences and dynamically updated medial-prefrontal
representations.

This is especially relevant to the present note because it makes sequence generation a
current, online part of planning/inference rather than merely a historical trace.

It still does not show that a person consciously targets a hippocampal replay loop.

### Phase can be causally manipulated

Kragel et al. (2025, Nature Communications,
DOI 10.1038/s41467-025-59417-7) used closed-loop stimulation timed to ongoing human
hippocampal theta. Phase-locked neocortical stimulation increased hippocampal theta during
stimulation and produced persistent increases in hippocampal-network connectivity.

So "phase is only decorative" is too strong. But stimulation-induced network changes do
not imply that ordinary recollection uses voluntary phase steering.

---

## 6. The mental-abacus example is real, but the strongest interpretation is unnecessary

Abacus mental calculation is not merely an internet trick.

Experimental and neuroimaging work describes a learned visuospatial / visuomotor strategy
in which users manipulate an internal abacus representation. In at least some trained
users, overt finger movements occur during mental calculation and interfering with finger
movement has been reported to impair performance. More expert users can eventually perform
the calculation without overt movement.

Relevant examples include:

- Ku et al. (2012), *Sequential Neural Processes in Abacus Mental Addition*, PLoS ONE,
  PMID 22574155;
- Tanaka et al. / later neuroimaging work summarized in the abacus literature;
- oscillatory MEG comparisons of abacus experts and novices (2020).

The useful lesson is not "finger motion drives a hippocampal oscillator."

It is much weaker and better:

> **a learned motor/visuospatial procedure can become part of the computational path by
> which an internal representation is made usable.**

That is exactly an active-reentry idea.

---

## 7. Enactment prevents an easy disease story

Action and memory are linked strongly enough that there is a large enactment-effect
literature: performing meaningful actions during learning typically improves later memory
relative to verbal study alone.

But this literature blocks a simplistic mapping such as:

```text
Alzheimer's -> broken action loop
schizophrenia -> broken action loop
```

A 2019 study of 32 mild-to-moderate Alzheimer participants found memory advantages from
subject-performed and experimenter-performed encoding relative to verbal encoding
(De Lucia et al., PMID 31311416).

An older schizophrenia study reported that the enactment advantage was nearly lost in its
patient sample (Daprati et al., 2005, PMID 15707912), but one study is not a disorder-wide
mechanism.

So the correct research decomposition is not "which disorder has bad loops?"

It is:

```text
storage / trace quality
control policy / ability to reinstate context
state-transition precision
receiver/readout geometry
phase/routing coordination
behavioral output
```

Different pathologies could affect different rows.

The old Geometric-Neuron and Deerskin results should therefore remain hypothesis
generators, not evidence for this decomposition.

---

## 8. A stronger interpretation of "I can set a loop in motion"

The useful systems reading of that sentence is not that introspection has direct access
to named hippocampal circuits.

It is:

> **the controller has actions that alter its own future observability.**

This is familiar in active sensing.

A robot turns its camera because the world state is not observable from its current
viewpoint.
A person moves an object because touch reveals a property vision does not.
A memory-search process may similarly change internal/external context because the target
is not observable from the present cognitive state.

That gives a more precise meaning to "re-live the sequence":

```text
current cue
   -> choose state-changing action / imagery / context
   -> internal trajectory changes
   -> a previously null component becomes potent
   -> partial recollection appears
   -> use that recollection as the next cue
   -> continue
```

Memory search can therefore be iterative active inference / state estimation rather than
a one-shot address lookup.

---

## 9. Connection to PerceptionLab

The PerceptionLab wave-field result established a much smaller primitive:

```text
one current state
contains consequences at several causal ages
```

This note adds a different axis:

```text
one current state
contains dimensions with different current readability

and the controller can alter that readability over time
```

Together:

```text
CAUSAL AGE
where is the consequence in its unfinished trajectory?

ACCESSIBILITY
which part of that current state can this receiver read?

CONTROL
what trajectory can change what becomes readable next?
```

This is a more useful three-coordinate picture than a scalar "width of the present".

---

## 10. Immediate AI translation: re-entry policies

This gives `WidePresent` a local, non-LLM direction that does not need a paid API.

An asynchronous agent can lose practical context even if an event log still exists.
The ordinary solution is "stuff more transcript back into context."

The control/observability version asks instead:

> **what minimal action sequence would reconstruct the task state?**

Examples:

```text
open the last edited file
inspect the current diff
query the pending job
re-read the last failing test
re-run a deterministic probe
look at the object currently selected in the UI
```

Those are **re-entry policies**.

A process-present record could therefore carry not only:

```text
fact
age
source
pending/completed
receiver frontier
```

but optionally:

```text
reentry_probe
reentry_cost
expected_information_gain
superseded_by
```

Then context recovery becomes active state estimation.

This is much closer to a product primitive than another temporal embedding.

---

## 11. The local AI gate to build next

Do not use an LLM first.

Construct two hidden worlds with the same completed transcript and the same cached facts.
The worlds differ only in latent current task state.

Give the agent several possible probe sequences.

Compare:

```text
A. transcript-only decision
B. one random probe
C. unordered bag of the right probes
D. learned / stored re-entry sequence
E. omniscient state
```

Score:

```text
decision accuracy
probe cost
steps to disambiguation
robustness when one probe is missing
robustness to order scrambling
```

The load-bearing result would not be that active sensing works; that is known.

The useful result would be whether a **small reusable process-present record can store a
cheap re-entry policy that resolves state aliasing better than replaying a large passive
history**.

That is an engineering question worth answering locally.

---

## 12. Brain-side falsification gate

The strongest brain claim worth testing is now narrower than "memory rides loops":

> **Successful retrieval should sometimes be preceded by a state trajectory that
> increases target-specific observability, and reinstating the relevant action/context
> trajectory should improve that observability beyond matched nonspecific movement or
> arousal.**

A useful experiment would therefore need:

```text
same memory material
same gross motor output / effort

condition A: congruent encoding/retrieval trajectory
condition B: action-order scrambled trajectory
condition C: matched unrelated movement
condition D: no movement / imagery only
```

and neural readouts that ask when target information becomes decodable, not merely
whether oscillatory power changed.

If order-congruent re-entry provides no advantage over matched movement/context once
attention and arousal are controlled, the strong trajectory-control idea should be
downgraded.

---

## 13. Current synthesis

The project began with:

> I do not live in an instant.

PerceptionLab sharpened that into:

> one current state can contain unfinished consequences of different causal ages.

The subspace work added:

> not every currently active degree of freedom is visible to every receiver.

The re-enactment observation now adds:

> **the organism can sometimes act on itself or its context in order to change what will
> become visible next.**

So the emerging object is no longer a "wide present" in the simple sense.

It is closer to a **controlled accessibility geometry**:

```text
current latent state
+ causal ages
+ receiver-specific readout
+ phase/routing state
+ available control trajectories
```

A memory is not simply `present` or `absent` inside that object.

It can be:

```text
present but null
present and waiting for phase
present and recoverable by re-entry
present and already potent
or genuinely degraded / gone
```

That distinction is the piece worth keeping.
