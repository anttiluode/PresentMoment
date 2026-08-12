# Signals in flight: a spatially thick present

There is a second way for an instantaneous organism state to contain recent history besides slow biochemical ringdown:

> **finite propagation speed means that signals from different source times can coexist at different physical locations right now.**

This is ordinary delay-line physics, but it gives a literal interpretation of part of the `PresentMoment` intuition.

---

## 1. An axon is not an instantaneous edge

A graph diagram usually draws

```text
A ------> B
```

as if the edge has no state.

A physical axon has length and finite conduction velocity.  In the simplest nondispersive approximation, activity at position `x` and current time `t` reflects source activity from

```text
t - x/v
```

So the complete spatial state of the axon at one instant contains a short segment of the source's recent history.

```text
source                                              target
 t-now      t-dt      t-2dt      t-3dt      ...      t-delay
   |----------|----------|----------|------------------|
              all of these can coexist spatially NOW
```

The past has not been stored in a symbolic buffer.  Some consequences of the past are literally still travelling.

---

## 2. Delay systems require a history state

If a node receives delayed feedback,

```text
xdot(t) = F(x(t), x(t-tau), u(t))
```

then `x(t)` alone is not enough to determine its future.

The natural state includes a function over the recent interval:

```text
x_t(s) = x(t+s),  s in [-tau, 0]
```

Equivalently, if the whole physical transmission line is included in the state, that history is represented spatially along the line.

This gives a precise sense in which a closed loop can have a temporal thickness even at one clock instant.

This mathematics is standard delay-system theory; it is not a novelty claim.

---

## 3. Brain-body loops make the pipeline heterogeneous

A closed organism loop can contain several qualitatively different delays:

```text
neural conduction
+ synaptic/receptor kinetics
+ muscle/organ mechanics
+ circulation
+ endocrine kinetics
+ sensory transduction
+ return conduction
```

At one instant, different parts of this loop can therefore be carrying consequences launched at different past times.

A schematic threat loop might simultaneously contain:

```text
NOW
 |
 +-- current cortical appraisal
 +-- descending autonomic command launched milliseconds ago
 +-- cardiovascular consequence of an earlier command
 +-- afferent heartbeat/baroreceptor signal returning now
 +-- slower endocrine state launched minutes ago
 +-- episodic association reactivated by the returning body state
```

This is a distributed causal pipeline, not a single neural clock.

---

## 4. Axonal delay is not always perfectly fixed

Human intracranial stimulation data show that cortico-cortical axonal conduction delays are commonly in the millisecond-to-tens-of-milliseconds range (PMID 35416942).

A separate biophysical/experimental study in an unmyelinated crustacean axon showed that conduction delay itself can depend on recent activity on burst and minute timescales (PMID 28691900).

The latter is not evidence that human long-range axons implement the proposed temporal code.  It is a useful proof of principle:

> even propagation delay can be a state-dependent dynamical variable rather than a fixed timestamp offset.

That matters because a fixed delay line is again a known linear temporal basis; history-dependent delay moves toward the state-dependent dynamics being examined elsewhere in this repository.

---

## 5. A useful hierarchy

The emerging candidate `present` has at least four physical carriers of history:

```text
1. signals in flight
   milliseconds -> perhaps longer in peripheral pathways

2. fast recurrent neural / neuromodulatory state
   milliseconds -> seconds

3. mechanical/autonomic ringdown
   beats, breaths, vascular and metabolic dynamics

4. endocrine / slower physiological ringdown
   seconds -> minutes -> longer
```

The exact ranges are empirical and should not be baked into the theory.

The important point is heterogeneity.

---

## 6. Connection to sensory deprivation

Reducing external sensory drive does not remove these endogenous states.

It changes the ratio:

```text
external forcing
-----------------
endogenous pipeline + ringdown
```

If external forcing becomes weak, internally generated signals may become easier to detect or more strongly weighted.  But deprivation can also trigger homeostatic gain adaptation, so it is not a passive 'look at the internal system' experiment.

This gives two regimes:

```text
short deprivation:
    expose current endogenous state / alter relative weighting

longer deprivation:
    the system itself adapts its gain and potentially its dynamics
```

That distinction is important for interpreting anechoic-chamber, earplug and Floatation-REST results.

---

## 7. Current synthesis

The original image was a wide strip of time stored around `now`.

The more physical picture is now:

> **At one instant, the organism is a spatially distributed collection of signals-in-flight, cyclic phases, fading modes and state-dependent feedback loops.  Those current variables are residues and continuations of different past moments.**

A clock-time sliver can therefore contain a temporally extended causal state.

The question for `PresentMoment` is not whether this is true in the trivial physical sense—it is—but whether the nervous system *uses* that distributed state as a temporal basis for present cognition and action in a way not captured by ordinary fixed recurrent memory.
