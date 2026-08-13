# Actuality anchor — one live loop among many internal models

## Status

Working synthesis.  This is **not** a theory of phenomenal consciousness.

It follows from a problem created by `VIRTUAL_MACHINERY_AND_CONTROL_HANDLES.md`:

> if a learned brain can internally instantiate absent tools, actions, routes and other
> people, what distinguishes those counterfactual processes from the organism's actual
> ongoing state?

The provisional answer is a functional object called an **actuality anchor**.

---

## 1. The problem appears only after internal models become rich

A simple reactive controller need not maintain many counterfactual worlds.

A model-rich organism can simultaneously contain processes corresponding to:

```text
the cup that is physically in front of me
an imagined cup in another room
a remembered cup from yesterday
a predicted cup after I reach
a simulated other person's view of the cup
```

All can influence neural activity now.

Therefore:

```text
represented now
    !=
physically actual now
```

The mental-abacus example makes this vivid.  An internally reinstated abacus can support
real calculation even though no physical abacus is present.

So an organism capable of useful offline emulation needs some way to keep track of
which stream is currently coupled to real consequences.

---

## 2. Candidate definition

Call the **actuality anchor** the currently privileged closed loop whose predictions are
continuously corrected by this organism's live sensory/interoceptive consequences and
whose selected motor commands can change those consequences.

Schematically:

```text
                         offline internal models
                    / imagined tool / person / route \
                   /                               \
                  v                                 v
            predicted states                  predicted states

                         LIVE ORGANISM LOOP

      motor command ------------------------------+
           |                                      |
           v                                      |
      body / world                                |
           |                                      |
           v                                      |
   proprioception / vision / touch / interoception|
           |                                      |
           +-------- live prediction error -------+
```

The important asymmetry is not representational richness.

It is **closed-loop causal accountability**.

An imagined person can predict what a person might say.  Their internal hand does not
normally own the organism's actuators or receive the unforgeable stream of sensory
consequences generated when this organism actually moves.

---

## 3. This is old territory in motor control, not a new primitive

Forward-model / efference-copy theories already explain how self-generated action is
paired with predictions of its sensory consequences.

A particularly clean phenomenon is sensory attenuation: self-generated touch is
perceived differently from physically similar externally generated touch because motor
commands predict upcoming sensory consequences.

Kilteni et al. (eLife 2019, DOI `10.7554/eLife.42888`) further showed that this temporal
prediction can rapidly retune when the delay between action and touch is systematically
changed.

Inner speech provides a striking offline extension.  Whitford et al. (eLife 2017, DOI
`10.7554/eLife.28197`) found neurophysiological evidence consistent with a content- and
time-specific efference-copy-like prediction during inner speech.

So:

```text
self-generated / internally generated prediction
           +
comparison with actual sensory consequence
```

is established science.

The only useful role of `actuality anchor` is to connect that machinery to the broader
problem created by multiple concurrently callable internal models.

---

## 4. Actuality is not identical to agency

The sense of agency is itself fallible and separable.

Experiments with delayed/noisy virtual-hand feedback show that people's agency judgments
change with action–outcome evidence and need not behave like metacognitive confidence
judgments (Constant, Salomon & Filevich, eLife 2022, DOI `10.7554/eLife.72356`).

So the actuality anchor should not be defined as:

```text
whatever I consciously feel I caused
```

The live causal loop can remain real even when conscious attribution is wrong.

Likewise a dream can feel actual while external sensorimotor coupling is radically
changed.

That makes phenomenology a poor ground-truth label for the functional object.

---

## 5. The subject-index and actuality-anchor are related but not identical

`SUBJECT_INDEX_AND_TINY_CONTROL.md` proposed a weaker functional object:

> a common reference with respect to which action-conditioned futures are evaluated.

That is the **control index**.

The actuality anchor adds a constraint:

```text
CONTROL INDEX
    which organism/body/needs are these futures about?

ACTUALITY ANCHOR
    which current stream is being corrected by the live consequences of that organism?
```

Normally they should coincide.

But interesting states may pull them apart:

```text
dreaming
virtual reality
rubber-hand/body-ownership illusions
locked-in/paralysis
deafferentation
out-of-body/autoscopic phenomena
hallucination
motor imagery
inner speech
```

Those are experiments, not annoying exceptions.

---

## 6. Why this could generate something first-person-shaped without explaining experience

A controller with many internal models has a bookkeeping requirement.

Predictions have very different meanings depending on their source:

```text
if the physical body moves, update the actual state
if an imagined body moves, update a counterfactual state
if a remembered person speaks, do not treat it as current acoustic input
if an expected sound fails to arrive, generate a prediction error
```

This demands source/context information.

For action, all counterfactual futures also need a common reference:

```text
what happens to THIS controlled organism if action X is released?
```

That provides a functional route to a first-person-like origin:

> **one trajectory among many is privileged because it is the trajectory whose errors
> currently matter for updating and controlling this living body.**

This can explain why a control architecture needs an `actual / here / this-body`
reference.

It does not explain why that reference is experienced from the inside.

---

## 7. Relation to tiny control

The actuality anchor also clarifies how compact handles can have large effects.

A high-level handle need not micromanage the body:

```text
GO FOR A RIDE
```

can release a learned policy containing thousands of lower-level corrections.

What keeps the policy from becoming a mere fantasy is the live loop:

```text
launch policy
    -> body changes
    -> world/body feedback arrives
    -> prediction errors correct the policy
    -> next action is conditioned on the actual state
```

By contrast:

```text
IMAGINE GOING FOR A RIDE
```

can invoke parts of the same learned transition system while suppressing ordinary
motor output and relying more heavily on internally generated state transitions.

The two may share machinery but differ in how tightly the trajectory is coupled to the
actuality anchor.

---

## 8. New subtraction axis

The mental-abacus lesion case suggests that these should be separated:

```text
knowledge of the tool
physical skill with the tool
offline ability to instantiate the tool's transition dynamics
```

Likewise, future lesion/stimulation work should ask separately whether a person can:

```text
recognize X
remember facts about X
act with X when X is present
simulate/predict X when X is absent
use X to change a current decision
```

The last two are especially relevant to the current control surface.

A learned emulator can disappear without the subject disappearing.

---

## 9. Falsifiers / collisions

Do not keep `actuality anchor` if ordinary established language does the job better.

Mandatory comparisons include:

```text
forward models / efference copy
source monitoring / reality monitoring
predictive processing
active inference
body ownership / agency comparator models
```

The term earns a place only if explicitly joining these to `PresentMoment`'s
receiver-relative, asynchronous control question produces a measurable prediction that
the established formulations do not already make.

Strong falsifier:

> if live-vs-counterfactual source identity adds no predictive value once ordinary
> sensory prediction error and task context are represented, delete the construct.

---

## 10. Current working sentence

> **A model-rich organism can run many absent worlds internally, but only one ongoing
> stream is normally closed through the organism's live sensors, homeostatic
> consequences and actuators.  That privileged error-corrected loop may supply a
> functional actuality anchor around which first-person control is organized.  It can
> explain why control needs a `this organism / now` reference without explaining why
> there is something it is like to be that reference.**
