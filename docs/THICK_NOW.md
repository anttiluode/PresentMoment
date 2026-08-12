# A thin instant can contain a thick now

The central correction to the original `WidePresent` picture is this:

> **The present does not have to occupy a literal strip of past clock time in order to contain information about the past.**

At one mathematically instantaneous time `t`, a living organism has a very large state:

```text
X(t) = [
    neural activity,
    synaptic / neuromodulatory state,
    cardiac phase and mechanics,
    vascular state,
    respiratory phase,
    muscle / proprioceptive state,
    sympathetic / parasympathetic state,
    metabolic state,
    endocrine state,
    immune state,
    ...
]
```

Many components of `X(t)` are not functions of the external world *only at t*.
They are filters of what happened before.

So a present can be:

```text
thin in clock time
but
thick in causal state
```

This may be a cleaner physical interpretation of a `wide present` than a literal sliding matrix of old snapshots.

---

## 1. State-space form

A minimal linearized model is

```text
dX/dt = A X + B u(t)
y(t)   = C X
```

After a past perturbation `u`, current state contains

```text
X(t) = integral exp(A * s) B u(t-s) ds
```

The matrix exponential is the system's bank of fading histories.

Its eigenmodes determine which perturbations disappear quickly and which ring for longer.

This gives us a more rigorous meaning of present width:

> **Present width is related to the spectrum of causal modes that remain observable and behaviorally effective at now.**

There need not be one width.

---

## 2. Danger may change the system, not merely the input

The naive picture says:

```text
danger = larger input pulse
```

A more interesting possibility is:

```text
danger changes A, B and C
```

In words, arousal can potentially alter:

- the gain with which some inputs enter the system;
- the persistence of some state variables;
- which body channels strongly influence the brain;
- which memories are written strongly;
- which memories are retrievable from the current state;
- the weighting of immediate versus more remote consequences.

Then danger need not create a longer sensory integration window.
It can **reshape the impulse response of the organism**.

This is the dynamical version of saying that danger might alter gain, persistence, segmentation or predictive weighting rather than simply making time run slowly.

---

## 3. Axons are part of the loop, but axon length is not the whole width

A descending neural command can leave the CNS, alter an organ, and return through sensory afferents.

```text
brain
  |
  | efferent axons
  v
body dynamics
  |
  | afferent axons
  v
brain
```

The round trip contains several sources of temporal structure:

```text
propagation delay
+ synaptic / release kinetics
+ organ mechanics
+ cyclic phase
+ chemical kinetics
+ receptor dynamics
+ feedback gain
```

The important point is therefore not simply "long axons make a long present."

The stronger statement is:

> **A closed brain–body loop carries its own delay and impulse-response spectrum.**

Longer-lived organ and endocrine dynamics can preserve effects far beyond the neural conduction delay itself.

---

## 4. Body state as a temporal coordinate system

There are at least three qualitatively different temporal bases in the organism.

### Fading coordinates

Leaky variables can encode how recently a perturbation occurred:

```text
b_i(t) ~ exp(-age / tau_i)
```

A bank of different `tau_i` values gives a distributed history code.

This mathematics is not new. Scale-invariant memory models already construct temporal history from banks of leaky integrators and interpret them in Laplace-transform terms.

The question here is whether **peripheral physiological variables instantiate useful members of that bank and return them to neural computation.**

### Cyclic coordinates

Heartbeat and respiration add phase variables:

```text
phi_heart(t)
phi_resp(t)
```

These are not fading memories. They identify where the organism currently is in recurrent body cycles, and human experiments show that stimulus processing can depend on those phases.

### Boundary / reset coordinates

Arousal and event boundaries can alter how adjacent experience is partitioned and encoded.

So the candidate present basis is not one homogeneous buffer. It is a mixture of:

```text
fading traces
+ recurrent phases
+ event boundaries / resets
+ prospective neural predictions
```

---

## 5. Somatic observability

This leads to a control-theoretic question.

Suppose the brain sees only current body state `B(t)` and current external input.
How much can it infer about what happened recently?

Call this informally **somatic observability**:

> How identifiable is recent causal history from the organism's current bodily state?

The toy in `experiments/ringdown_age_decode.py` tests the smallest possible case.

One decaying body channel cannot reliably separate:

```text
strong old event
from
weak recent event
```

because both can produce the same present amplitude.

Several differently decaying channels can break that ambiguity because event magnitude is common while age affects each time constant differently.

Thus an event-age signal can emerge from **relative ringdown**, even when no component stores an explicit timestamp.

This is algebraically expected. The biological question is whether any real interoceptive system exploits an analogous relationship.

---

## 6. The body can be a memory key, not only a memory store

There is another possibility that matters for the parachute example.

The body does not need to contain a symbolic memory saying:

```text
I am falling from an aircraft.
```

Instead:

```text
threat event
   |
   v
body / neuromodulatory state
   |
   v
that state biases or cues associative memory
   |
   v
relevant episode / rule becomes active
   |
   v
pull the cord
```

Then the physiological state is part of the **address** used to recover a semantic memory rather than being the semantic memory itself.

This is much closer to the evidence on interoceptive context and fear memory than the claim that the brain explicitly reads a label saying "adrenaline high."

---

## 7. The loop can extend through the world

The largest loop is not necessarily brain -> body -> brain.

It can be:

```text
brain
  -> motor axon
  -> body
  -> world
  -> sensory consequence
  -> body receptors
  -> brain
```

For a parachutist:

```text
threat appraisal
 -> autonomic state
 -> motor decision
 -> hand pulls cord
 -> parachute / world state changes
 -> vestibular + visual + proprioceptive consequences
 -> new brain state
```

The environment has become part of the recurrent dynamics.

This is not a claim that extended cognition is new. It gives `PresentMoment` a precise warning:

> Do not assume the causal state defining `now` is confined to the skull.

---

## 8. Brain-only non-Markovian, organism-level Markovian

A useful mathematical perspective is that if we observe only brain variables, delayed bodily returns can look like mysterious memory terms:

```text
brain_next = F(brain_now, brain_past, ...)
```

But after enlarging the state to include the relevant body variables:

```text
[brain, body]_next = G([brain, body]_now, input_now)
```

much of that apparent history dependence can become ordinary current-state dynamics.

This yields the strongest conceptual sentence so far:

> **The organism may not need to store the recent past as snapshots because part of the recent past is still physically unfolding as the organism's present state.**

---

## 9. Consequence for AI

A language model's hidden state is normally advanced when computation is invoked.
A body-like dynamical substrate can evolve *between* externally supplied events.

A minimal artificial organism could therefore have:

```text
neural controller
      |
      v
continuous body ODE
   |        |
   |        +--> oscillatory coordinates
   +-----------> fading coordinates
      |
      v
interoceptive return
      |
      v
neural controller
```

This does not require pretending the AI is conscious.

It tests a concrete architectural question:

> Does an autonomous, continuously evolving closed-loop state give an online agent useful temporal structure that ordinary event-stepped recurrence does not?

Hard controls must include:

- explicit elapsed-time inputs;
- continuous-time RNN / SSM baselines;
- parameter-matched ordinary recurrence;
- body variables fed forward but not closed-loop;
- shuffled or delayed interoceptive return;
- equivalent banks of leaky traces implemented directly inside the network.

If those controls match the body loop, the AI architecture claim dies while the biological framing may remain valid.

---

## 10. Current hypothesis ladder

```text
H0  body variables have heterogeneous ringdowns
    -> already ordinary physiology

H1  current multichannel body state can encode recent-event variables
    -> mechanism sanity; easy to demonstrate synthetically

H2  the nervous system can read behaviorally useful temporal information from that state
    -> biological claim

H3  body feedback changes the causal temporal influence kernel of current cognition
    -> stronger biological claim

H4  arousal changes that kernel by modifying gain / persistence / segmentation
    -> danger / subjective-time link

H5  artificial closed-loop body state improves temporal agent behavior over strong continuous-time controls
    -> AI architecture claim

H6  any of this constitutes phenomenal present
    -> open; not implied by H0-H5
```

The project should move upward only when the lower rung survives.
