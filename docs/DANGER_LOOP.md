# Danger as a multiscale closed loop

This note develops one concrete case for the `PresentMoment` hypothesis: acute danger.

The claim is **not** that fear literally slows physical time or that one hormone creates a wider conscious window.

The useful question is:

> After a dangerous event perturbs the organism, which parts of that event remain causally active in the organism's current state, through which physical loops, and for how long?

---

## 1. The event does not end when the sensory stimulus ends

A simplified danger cascade is:

```text
threat cue
   |
   v
sensory / cortical / amygdala appraisal
   |
   +--------------------------+
   |                          |
   v                          v
fast neural recurrence    hypothalamic / brainstem output
                              |
                              v
                    sympathetic + adrenal response
                              |
              +---------------+----------------+
              |               |                |
              v               v                v
            heart          respiration       metabolism
              |               |                |
              +------- visceral afference -----+
                              |
                              v
                       NTS / brainstem
                              |
                       LC / limbic / cortex
                              |
                              +------> altered processing

and in parallel:

hypothalamus -> pituitary -> adrenal cortex -> glucocorticoids
      ^                                         |
      |                                         v
      +------------- brain feedback ------------+
```

These are not one loop with one latency. They are a family of coupled loops.

---

## 2. The parachute jump as an impulse-response experiment

Richter et al. (1996; PMID 8626864) measured first-time tandem parachutists from two hours before until one hour after the jump.

The interesting fact is the **ordering** of the physiological response:

```text
jump itself
    |
    +--> heart rate rises
    +--> plasma epinephrine rises

~10–20 min later
    |
    +--> norepinephrine peak
    +--> cortisol peak
    +--> GH / prolactin / TSH peaks

1 h later
    |
    +--> cortisol and TSH still elevated
```

This is almost exactly what one would ask for if trying to identify a physical system from its ringdown after an impulse.

The event has one external timestamp, but the organism carries a **trajectory of internal timestamps** in the form of state variables with different delays and relaxation rates.

---

## 3. A body variable is a memory kernel even when nobody calls it memory

For a body state `b_i`:

```text
tau_i * db_i/dt = -b_i + g_i * u(t - d_i)
```

where:

- `u(t)` is an event-related neural/efferent drive;
- `d_i` is propagation/response delay;
- `tau_i` is relaxation time;
- `g_i` is coupling gain.

Then the value of `b_i` **now** contains weighted information about earlier `u`.

A bank of heterogeneous variables

```text
B(t) = [b_1(t), b_2(t), ... b_N(t)]
```

is therefore a physical temporal basis.

This statement is mathematically ordinary. The research question is whether biology **uses** this basis in ongoing cognition rather than merely tolerating it as physiological baggage.

---

## 4. The return path matters

The body becomes relevant to cognition only if its state returns to neural computation.

Several classic results establish plausible routes.

### Peripheral epinephrine is not simply central epinephrine

Circulating epinephrine is largely excluded from the brain by the blood–brain barrier. Its cognitive effects therefore force us to look for peripheral intermediary routes rather than imagining direct entry into cortex.

Systemic epinephrine can increase amygdala norepinephrine (Williams et al., 1998; PMID 9926823).

Noradrenergic blockade in the NTS attenuates the memory-enhancing effect of peripheral epinephrine (Miyashita & Williams, 2003; PMID 14499960).

Peripheral vagal stimulation at a memory-modulating intensity increases norepinephrine output in basolateral amygdala (Hassert et al., 2004; PMID 14979784).

So one plausible functional chain is:

```text
peripheral arousal state
        |
        v
visceral / vagal signaling
        |
        v
NTS and associated brainstem pathways
        |
        v
central noradrenergic modulation
        |
        v
changed attention / encoding / memory
```

The exact route depends on the signal and should not be compressed into one universal pathway.

---

## 5. Heart and breath are fast recurrent coordinates of `now`

The feedback is not only minutes-long endocrine state.

### Cardiac phase

Garfinkel et al. (2014; PMID 24806682) presented fearful and neutral faces at different phases of the cardiac cycle. Fearful faces were more readily detected and judged more intense at systole than diastole, with corresponding differences in amygdala activity.

Garfinkel et al. (2020; PMID 33180532) showed that cardiac afferent timing also affects fear learning and memory.

So two external stimuli presented only fractions of a second apart can enter **different internal bodily states** even if their nominal visual content is identical.

### Respiratory phase

Human experiments also find respiratory-phase dependence in reaction time and emotional discrimination (Johannknecht & Kayser, 2022, PMID 35173204; Matsumoto et al., 2023, PMID 36715139).

A 2026 J. Neurosci. study further reports that people spontaneously adjust breathing relative to anticipated interoceptive and exteroceptive stimuli and that performance varies by respiratory phase (Della Penna et al., 2026, PMID 42045067).

This makes heartbeat and respiration candidate **phase coordinates inside the present state** rather than merely background physiology.

---

## 6. The hippocampus participates in a slow stress loop

Sapolsky, Krey & McEwen (1984; PMID 6592609) provided evidence that glucocorticoid-sensitive hippocampal neurons participate in terminating the adrenocortical stress response.

Sapolsky, Zola-Morgan & Squire (1991; PMID 1744687) later showed glucocorticoid hypersecretion after lesions involving the hippocampal formation in nonhuman primates, supporting a role for hippocampal systems in endocrine feedback.

This gives a useful conceptual crossing:

```text
HIPPOCAMPUS
   |
   +--> relations among events / episodic memory
   |
   +--> participant in a body-wide stress feedback system
```

The tempting hypothesis is that these roles interact.

The conservative position is that they may be parallel functions of the same structure.

Experiments must separate those possibilities.

---

## 7. Event boundaries may be another form of gain change

Clewett, Huang & Davachi (Neuron, 2025; PMID 40482639) found that event boundaries trigger pupil-linked arousal and locus-coeruleus-related responses that predict later memory separation, with boundary-related temporal pattern separation in hippocampal dentate gyrus.

That suggests a danger/arousal event need not make a sensory window literally longer.

It may instead change the **partitioning and gain** of the state:

```text
ordinary moment:
    weak boundary -> neighboring states blend more

salient / arousing boundary:
    strong reset -> adjacent event states separate more
                  -> memory trace becomes more distinctive
```

This is compatible with retrospective time dilation without requiring a faster sensory camera.

---

## 8. Four different meanings of "widen the present"

Do not collapse these into one effect.

### A. Persistence width

How long does a past perturbation continue to influence current state?

Measured by the tail of a causal influence kernel.

### B. Resolution / density

How many distinct internal state transitions occur per unit external time?

Arousal might make a short interval acquire more separable landmarks without extending the underlying sensory integration constant.

### C. Gain width

How strongly do recent traces influence current action or memory writing?

Arousal can increase the weight of a trace without changing its physical duration.

### D. Predictive width

How far ahead do current computations actively represent possible consequences?

Danger may shift the system toward immediate future consequences even while remote past processing is suppressed.

A good experiment must state which width it means.

---

## 9. Proposed measurable object: the organismal present kernel

Let `a(t)` be a current decision or neural state. Perturb information associated with an earlier time `t-Delta` while holding everything else fixed.

Define conceptually:

```text
K(Delta) = effect on a(t) of removing / changing state caused by t-Delta
```

Now repeat under body-channel interventions:

```text
K_intact(Delta)
K_cardiac-clamped(Delta)
K_respiration-clamped(Delta)
K_slow-endocrine-clamped(Delta)
```

If the body is part of the operative temporal state, these interventions should change the shape of `K`.

This is stronger than showing that heart rate correlates with fear or that cortisol changes memory.

---

## 10. A computational translation

For an artificial agent, do not immediately give it a symbolic `fear=0.72` variable.

Give it a small synthetic body:

```text
agent output
   |
   +--> fast actuator state
   +--> oscillator 1
   +--> oscillator 2
   +--> slow leaky state
   +--> very slow leaky state
              |
              v
        interoceptive readout
              |
              +----> agent input
```

Then ask whether the closed loop provides anything that equally sized ordinary recurrence does not.

Hard controls:

1. same information with explicit elapsed-time features;
2. parameter-matched GRU / SSM;
3. feed-forward body state without return loop;
4. shuffled body return;
5. fixed versus adaptive coupling gain.

If the body loop loses, the biological story may still be true while the AI architecture is unnecessary.

---

## Current candidate sentence

> **A living present may be partly constituted by somatic ringdown: external events launch multiscale brain–body trajectories whose returning interoceptive and endocrine consequences remain causally available to the computation occurring now.**

That is a hypothesis, not yet a result.
