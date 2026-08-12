# Public and private subspaces — a possible answer to partial maturity

The KYY deadline experiment exposed a problem with the simple statement:

> the brain can propagate unfinished computation, therefore unfinished computation can
> be used downstream.

Those are not the same claim.

In the local scatter toy, ordinary final-only training produced intermediate states
that already contained the task answer in a linearly decodable form, yet the model's
**own final readout** often interpreted those states catastrophically incorrectly.

So partial computation requires a second property:

> **some task-relevant projection must remain meaningful to the receiver while the
> larger internal state continues to evolve.**

Neuroscience already has closely related population-level mechanisms.

---

## 1. Output-null and output-potent activity

Kaufman, Churchland, Ryu & Shenoy (2014), *Cortical activity in the null space:
permitting preparation without movement* (Nature Neuroscience 17, 440-448,
DOI 10.1038/nn.3643), asked a simple puzzle.

Motor cortical areas are active during movement preparation, before the muscles move.
If muscle activity is downstream of motor-cortical activity, why does this preparation
not cause premature movement?

Their population-level result supports a decomposition into:

```text
output-null patterns
    internal cortical activity that largely cancels in the downstream muscle readout

output-potent patterns
    population activity aligned with the dimensions that actually drive output
```

This is useful for `PresentMoment` because it demonstrates that the brain does not need
to make an entire population state "finished" or externally meaningful at once.

A large amount of computation can evolve in dimensions that are temporarily private
to the upstream circuit.

---

## 2. Communication subspaces between cortical areas

Semedo et al. (2019), *Cortical areas interact through a communication subspace*
(Neuron 102, 249-259.e4, DOI 10.1016/j.neuron.2019.01.026), simultaneously examined
population activity in interconnected visual cortical areas.

V2 fluctuations were related not to every prominent pattern in V1, but to a
**low-dimensional subset of V1 population activity patterns**.

The useful schematic is:

```text
             V1 population state
          /          |           \
     private       private       public
     dynamics      dynamics      communication subspace
                                  |
                                  v
                                 V2
```

The largest internal fluctuation directions in V1 need not be the directions most
strongly communicated to V2.

So "what is present in an area" and "what is currently legible to the next area" are
already distinct biological questions.

---

## 3. A public/private version of the thick now

The earlier `PresentMoment` picture emphasized several ways the current organism state
can carry recent history:

```text
fading modes
signals in flight
body/world feedback
cyclic phase
mixed computational maturity
```

The subspace literature adds another axis:

```text
private state
    currently active but weakly coupled to the receiver

public state
    current projection that has causal leverage on the receiver
```

Let a large source population have state `x(t)` and a downstream readout/coupling `C`:

```text
y(t) = C x(t)
```

Then changes `delta x` satisfying

```text
C delta_x ~ 0
```

can support substantial internal computation without materially changing downstream
output.

Changes with

```text
C delta_x != 0
```

are output-potent / communicable.

The `now` is therefore not one giant vector whose every coordinate must have the same
semantic maturity.

A better picture is:

```text
X_now = [ private evolving dynamics | public readable projection ]
```

Both exist now.
Only part of the state is currently exposed to a given receiver.

---

## 4. This resolves part of the "unfinished vectors" problem

A synchronized software architecture often behaves as if a whole block must complete
before the next block consumes its output.

A biological network need not use that convention.

But a barrier-free system faces a different problem:

```text
if everything propagates immediately,
why does unfinished internal activity not constantly corrupt downstream behavior?
```

The null/potent and communication-subspace picture suggests one answer:

> **most ongoing computation can remain in receiver-null dimensions while a smaller
> projection carries whatever is currently safe/useful to expose.**

This is not the same as a hard gate.
The receiving population can remain continuously coupled.
What changes is the geometry of which source activity patterns couple effectively.

That is much closer to continuous flow than to waiting for a `DONE` flag.

---

## 5. The KYY diagnostic now has a biological interpretation

In the scratch `geom_scatter` reconstruction:

```text
ordinary final head on early phases          often very poor
separate linear probe fitted to each phase   nearly perfect
```

That means the target variable was already available in the population state, but in
phase-dependent coordinates.

A downstream unit with one fixed set of weights would therefore fail.

This is almost the inverse of a stable communication subspace.

The phase-supervised KYY variant asked the same shared readout to remain useful across
ordinary phase boundaries.  It then generalized surprisingly well to asynchronous
mixed-maturity states that it never saw during training.

That suggests an engineering translation of the biological subspace idea:

```text
large hidden state may keep moving
            |
            +--> task-relevant low-dimensional projection remains aligned
```

The key property is not that every hidden coordinate remains stable.
It is that the **receiver-relevant projection** remains legible.

---

## 6. Important opposite case: sometimes you WANT computation to stay null

Kaufman's motor result also prevents an overenthusiastic interpretation.

There are times when an unfinished result should **not** propagate into action.

Preparation can be useful precisely because it remains output-null until an appropriate
transition into potent dimensions.

So a good asynchronous organism needs both capabilities:

```text
continuous early communication when partial evidence is useful
                +
output-null computation when premature expression would be harmful
```

This is richer than "no barriers is better."

The nervous system may be managing **causal visibility**, not simply maximizing it.

That connects naturally to the earlier sensory-deprivation and neuromodulatory work:
state may change which internal dimensions have causal leverage without requiring the
underlying memory to disappear.

---

## 7. A possible new state descriptor: causal visibility

For source state `x` and receiver `j`, define only as a descriptive object:

```text
V_j(t) = receiver-relevant projection / coupling of current source dynamics
```

There need not be one universal public subspace.

The same source activity can be:

```text
potent for receiver A
null for receiver B
```

So the biologically thick present may be **receiver-relative**.

Something can be physically present in the organism, actively changing, and still not
be part of the current control present for a particular downstream system.

This sharpens the earlier distinction:

```text
trace exists
    !=
trace is decodable in principle
    !=
trace is legible to this receiver
    !=
trace currently changes behavior
```

Those are four different claims.

---

## 8. A stronger AI experiment than "deep-supervise everything"

Deep supervision after every phase is useful diagnostically, but it can be too blunt.
It may pressure the whole computation to become answer-ready too early.

A more brain-shaped experiment would explicitly separate:

```text
private/null dimensions
public/potent dimensions
```

Then allow unrestricted local dynamics in the private subspace while asking only a
small shared public projection to maintain calibrated semantics across maturity.

For example:

```text
h(t) = h_private(t) + h_public(t)

readout sees primarily h_public
internal recurrence uses both
```

Compare:

```text
A. final-only KYY
B. deep supervision of the final task at every phase
C. small stable public subspace + free private dynamics
D. phase-specific exit heads
```

The interesting questions are:

- can C preserve final accuracy while making arbitrary deadlines useful?;
- does C need fewer constraints than full deep supervision?;
- can task-relevant information enter/leave the public subspace when appropriate?;
- does a premature-response task reward keeping uncertain computation null?;
- does the same learned public projection survive delay-warp OOD?;

This would test a concrete systems principle rather than claiming to recreate cortical
communication.

---

## 9. Connection to recent dynamic-geometry work

Recent human EEG work on flexible action selection emphasizes almost the same tension:
neural population geometry can be strongly time-varying, yet reliable action requires
task-critical information to become stable enough for a temporally robust downstream
readout.  A 2024 Nature Communications study reported a transient expansion of
representational geometry followed by stabilization of task-relevant subspaces before
successful responses (DOI 10.1038/s41467-024-52777-6).

Again, this is not evidence for the KYY mechanism.

It is evidence that the problem we accidentally exposed in KYY —

```text
rich evolving internal geometry
versus
stable downstream meaning
```

—is a real systems problem in neuroscience as well.

---

## 10. Current synthesis

The earlier sentence was:

> A physical medium can give you unfinished computation for free. Meaning is not free.

The subspace literature suggests a possible biological continuation:

> **Meaning does not have to be attached to the whole unfinished state. It can live in
> a low-dimensional public projection while the rest of the system keeps computing.**

That is a much more plausible architecture for a barrier-free `now`.

The next experiment should therefore stop asking whether every intermediate vector is
readable and ask:

> **How small can the continuously legible public subspace be while the private local
> dynamics remain free to evolve?**
