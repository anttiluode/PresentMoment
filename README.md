# PresentMoment

**Researching whether the biological `now` is partly implemented by a distributed, multiscale brain–body feedback state.**

The starting intuition is simple:

> I do not seem to live in an infinitesimal instant.

`WidePresent` attacked one AI-agent interpretation of that intuition and correctly collapsed much of it into ordinary temporal validity bookkeeping. This repository asks a different question:

> **What physical state does a living organism carry at one moment, and how much recent history is still causally present inside that state?**

No claim about consciousness is assumed. The target is a measurable dynamical object.

---

## The new hypothesis: the body is part of the temporal state

A neural event does not necessarily stay inside the brain.

A threat can cause descending autonomic output, adrenal secretion, cardiovascular and respiratory changes, muscle tension, metabolic changes and endocrine responses. Those changed bodily states are sensed again through visceral afferents and humoral routes and can alter brainstem, neuromodulatory, limbic and cortical processing.

So a simplified loop is:

```text
external event
     |
     v
brain / appraisal
     |
     +------ fast recurrent neural state -------------------+
     |                                                      |
     v                                                      |
autonomic / endocrine output                               |
     |                                                      |
     v                                                      |
heart / vessels / lungs / adrenal / metabolism / immune    |
     |                                                      |
     v                                                      |
interoceptive afference + circulating slow signals         |
     |                                                      |
     v                                                      |
NTS / LC / hypothalamus / amygdala / hippocampus / cortex -+
```

The body is therefore not merely an actuator attached to a brain. It can be an **intermediate dynamical medium in a closed recurrent loop**.

---

## Somatic ringdown

The strongest motivating observation so far comes from a classic acute-stress experiment using first-time tandem parachute jumps (Richter et al., 1996, PMID 8626864).

The same event produced physiological responses at different latencies:

- heart rate and plasma epinephrine increased during the jump;
- norepinephrine, cortisol, growth hormone, prolactin and TSH peaked roughly 10–20 minutes later;
- cortisol and TSH remained elevated an hour after the jump.

That is naturally described as a **multiscale ringdown** after a perturbation.

The event is gone, but the organism is not back at its pre-event state. At each later instant, its current physiological vector contains a different residue of the event.

This suggests a precise computational framing:

> **The present organism state may act as a bank of causal temporal traces.**

Not a symbolic timestamp. Not necessarily an explicit memory. A physical residue.

---

## Minimal model

Let an output from the brain be `u(t)`. A body variable `b_i` with delay `d_i` and relaxation time `tau_i` can be written as

```text
tau_i * db_i/dt = -b_i + g_i * u(t - d_i)
```

so that its current value is a weighted convolution of earlier input:

```text
b_i(t) ~ integral exp(-s/tau_i) * u(t - d_i - s) ds
```

With many body variables:

```text
B(t) = [b_fast(t), b_cardiac(t), b_resp(t), b_metabolic(t), b_endocrine(t), ...]
```

`B(t)` is a multiscale representation of recent causal history even if the external stimulus is identical at the current instant.

The afferent return closes the loop:

```text
brain_state(t+dt) = F(brain_state(t), sensory_now(t), interoception(B(t)))
```

This is the key object in this repository.

---

## Important biological correction

The loop should **not** be described as "the brain secretes adrenaline, adrenaline enters the brain, and the brain reads it back."

Peripheral epinephrine is largely excluded from the brain by the blood–brain barrier. Yet peripheral epinephrine can influence memory through body-to-brain routes, including pathways involving the nucleus of the solitary tract (NTS), vagal afference, and central noradrenergic modulation.

Classic experiments found that:

- systemic epinephrine elevates norepinephrine release in the amygdala;
- blocking noradrenergic receptors in the NTS attenuates epinephrine's mnemonic effect;
- peripheral vagus stimulation at a memory-modulating intensity increases basolateral-amygdala norepinephrine output.

That makes the body loop more interesting, not less: the periphery is an actual intermediate system rather than a transparent wire.

Key papers:

- Williams et al. (1998), PMID 9926823
- Miyashita & Williams (2003), PMID 14499960
- Hassert, Miyashita & Williams (2004), PMID 14979784
- Liang, Juler & McGaugh (1986), PMID 3955350

---

## Sapolsky / McEwen connection

Robert Sapolsky trained in Bruce McEwen's neuroendocrinology laboratory. Their stress work is directly relevant because it treats brain and endocrine system as a **closed regulatory system**, not a one-way chain.

Sapolsky, Krey & McEwen (1984) showed that glucocorticoid-sensitive hippocampal neurons participate in terminating the adrenocortical stress response (PMID 6592609). Later primate work also supported a hippocampal role in glucocorticoid feedback (Sapolsky, Zola-Morgan & Squire, 1991, PMID 1744687).

So the hippocampus is interesting here twice:

```text
hippocampus as temporal / episodic memory machinery
                +
hippocampus as participant in a slow body–brain endocrine feedback loop
```

That overlap is worth attacking experimentally rather than treating as metaphor.

---

## Heartbeats and breaths can modulate the computation happening now

The body loop is not only slow endocrine chemistry.

Human experiments show that the phase of ongoing bodily cycles can change processing of external information:

- fearful faces are detected more readily and judged more intense at cardiac systole than diastole, with stronger amygdala responses (Garfinkel et al., 2014, PMID 24806682);
- cardiac phase during fear learning influences later fear memory (Garfinkel et al., 2020, PMID 33180532);
- respiration phase covaries with sensory-cognitive reaction time and can modulate emotional discrimination (Johannknecht & Kayser, 2022, PMID 35173204; Matsumoto et al., 2023, PMID 36715139).

So `now` is not merely a cortical vector indexed by wall-clock time. The computation at one nominal instant can depend on **where the body currently is in its own recurrent cycles**.

---

## A useful distinction: three widths

We should not make every lingering hormone part of the phenomenological present.

Keep at least three notions separate:

```text
1. phenomenal present
   what is experienced as happening now

2. control present
   currently active state variables that can alter the next perception/action

3. consolidation tail
   physiological/neural processes by which an event still changes later memory
```

The present hypothesis is initially about **(2)**. Whether that helps explain **(1)** is an empirical question.

---

## New definition of "width"

Do not define present width as a guessed number of seconds.

Define a causal influence kernel:

```text
K_t(Delta) = change in current decision/state when information from time t-Delta is selectively removed
```

Then the present has structure if `K_t(Delta)` is non-zero over a range of past and anticipated offsets.

The body-loop hypothesis predicts that perturbing or clamping specific physiological feedback channels changes that kernel.

A danger state may therefore change the present by changing **gain, persistence, segmentation or coupling**, not necessarily by making a sensory shutter literally longer.

---

## Prior-art guardrail

Many neighboring ideas already exist:

- interoception and predictive regulation;
- neurovisceral integration;
- stress neuroendocrinology;
- embodied cognition;
- morphological / physical reservoir computing;
- state-dependent and emotion-modulated memory;
- neural time cells and multiscale temporal integration.

So the claim cannot simply be "the body matters for cognition" or "the body has dynamics."

The narrower hypothesis worth testing is:

> **H_body-present:** Heterogeneous closed-loop body dynamics provide an online temporal basis that preserves behaviorally usable information about recent events and changes the causal temporal neighborhood of current computation.

If ordinary brain-only recurrence or explicit timestamps reproduce everything under equal information and parameter budgets, the special claim loses.

---

## First experimental ladder

### Gate 0 — ringdown sanity

Show, without training a fancy network, that a heterogeneous bank of delayed/relaxing body variables contains decodable information about a past perturbation after the external input has returned to baseline.

This is a mechanism demonstration, **not evidence of a biological discovery**.

### Gate 1 — closed-loop value

Same current sensory input and same explicit event history. Compare:

```text
A. brain-only recurrent state
B. brain + feed-forward body variables
C. brain <-> body closed loop
```

Ask whether C gives a robust advantage on tasks where delayed consequences matter.

### Gate 2 — phase intervention

Model cardiac / respiratory oscillators separately from slow endocrine traces. Randomize or clamp their phases while holding external input fixed. Measure changes in the causal present kernel.

### Gate 3 — arousal

Do **not** ask merely whether danger makes subjective time longer.

Ask which parameter changes reproduce known effects:

```text
more gain?
more segmentation?
longer persistence?
stronger memory write?
changed future weighting?
```

### Gate 4 — real physiology

Use paired physiological + behavioral data to ask whether current heart/respiration/autonomic state carries predictive information about recent events beyond explicit stimulus history and brain signals alone.

---

## Working picture

The current candidate is not a single chain anymore.

It is closer to a **bank of loops and ringdowns**:

```text
milliseconds : recurrent neural activity / axonal propagation
~heartbeat   : cardiovascular afferent phase
seconds      : respiration / fast autonomic state
seconds-min  : catecholaminergic and metabolic consequences
minutes+     : HPA / glucocorticoid state
longer       : consolidation, immune and plastic changes
```

The exact times above are intentionally schematic; the repository should use measured kinetics when a claim depends on them.

The organism's state at one instant is therefore a cross-section through many processes that began at different earlier times.

That may be one physical meaning of a **wide present**.
