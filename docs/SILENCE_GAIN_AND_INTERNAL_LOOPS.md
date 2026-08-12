# Silence, sensory deprivation, and internal-loop gain

The intuition to test is not:

> silence makes the nervous system go crazy because the ear has nothing to hear.

That is too strong and contradicted by part of the literature.

A better question is:

> **What happens to the gain and causal influence of endogenous brain/body loops when reliable exteroceptive drive is strongly reduced?**

This matters to `PresentMoment` because the proposed temporally thick `now` is not only a set of traces.  It is a closed system whose readout and dynamics can be state dependent.

---

## 1. Brief deprivation can expose internally generated percepts

Mason & Brady (2009; PMID 19829208) placed healthy participants selected for high or low hallucination proneness into brief light-and-sound sensory deprivation.  Psychotic-like experiences including perceptual disturbances increased under deprivation, with larger perceptual effects in the hallucination-prone group.

Follow-up work using an anechoic-chamber deprivation paradigm also found increased psychotic-like experiences and a state/trait interaction (Daniel et al., 2014/2015; PMID 25177302 / 25811027).

This is suggestive of a system in which reducing external constraint can make internally generated activity more behaviorally/perceptually visible.

It does **not** establish that deprivation simply increases recurrent gain, and it does not justify saying that people generically "go nuts" in silence.

---

## 2. Reduced environmental stimulation can also be calming

Floatation-REST strongly attenuates exteroceptive stimulation across multiple modalities.

In clinically anxious participants, a 90-minute Floatation-REST condition reduced anxiety and muscle tension while increasing awareness/attention to cardiorespiratory sensations (Feinstein et al., 2018; PMID 29656950).

A later physiological study found lower blood pressure and breathing rate and an autonomic shift consistent with lower sympathetic arousal during Floatation-REST (Flux et al., 2022; PMID 36570829).

Floatation-REST has also been associated with altered body boundaries and subjective time distortion (PMID 38654027).

So sensory reduction is not synonymous with instability.

A useful interpretation is **reallocation/reweighting**:

```text
strong exteroceptive drive
        |
        v
external channels dominate current state estimation

reduced exteroceptive drive
        |
        v
relative influence / visibility of endogenous and interoceptive channels changes
```

Depending on the controller, priors, trait state and timescale, that reweighting could produce relaxation, heightened interoceptive awareness, phantom percepts, or some mixture.

---

## 3. The auditory system supplies a literal gain-control example

Temporary auditory deprivation in normal-hearing adults is experimentally tractable.

Human earplug studies show adaptive changes consistent with central auditory gain modulation after reduced peripheral input (for example PMID 36599259, 30890481, 19640020, 27620512).

In Schaette et al. (2012; PMID 22675466), continuous unilateral earplugging produced reversible phantom auditory sensations in healthy volunteers.

This is close to the original intuition:

```text
less input from outside
        |
        v
homeostatic / adaptive gain change
        |
        v
internally generated activity becomes more consequential
```

But the strongest version is not "the ear loops back on itself."  The auditory system contains descending as well as ascending pathways, central homeostatic plasticity, spontaneous activity and cross-level gain control.  The loop is distributed.

---

## 4. PresentMoment interpretation: C can change before A changes

Using the linearized notation

```text
xdot = A x + B u
y    = C x
```

strong sensory reduction can affect several different objects.

### Input change only

```text
u_external -> 0
```

Nothing about the organism itself changes yet.

### Readout / weighting change

```text
C_external down
C_internal relative weight up
```

The same internal dynamics become more visible to perception/decision.

### Gain / input-coupling adaptation

```text
B or feedback gain changes
```

The nervous system compensates for reduced input.

### Dynamic reconfiguration

```text
A -> A(state)
```

The actual coupling/persistence of the recurrent system changes.

These should not be conflated.

The deprivation literature gives evidence that reduced input can be accompanied by changed perception, interoceptive awareness, autonomic state and auditory gain.  It does not by itself tell us which matrix changed in any one experiment.

---

## 5. Important algebraic guardrail: state-dependent rates are not enough

Suppose `A(state)` is diagonal in one fixed basis for every state:

```text
A_quiet  = diag(lambda_q1, lambda_q2, ...)
A_danger = diag(lambda_d1, lambda_d2, ...)
```

The rates can vary with state, but all modes remain separate and the operators commute.

That is a time-varying exponential bank, not a strong geometric escape.

The sharper condition is:

```text
[A(state_1), A(state_2)] != 0
```

or equivalently, the relevant transition operators cannot all be reduced to one shared modal basis.

Then path matters:

```text
danger -> calm
```

can leave a different current state from

```text
calm -> danger
```

although the same durations were spent in each state.

`experiments/state_dependent_loop_order.py` is the minimal sanity check.

This is standard switched/bilinear-systems mathematics.  The research question is whether biologically meaningful state changes (arousal, neuromodulation, interoceptive feedback, sensory deprivation) exploit this kind of noncommuting reconfiguration in ways that matter for temporal computation.

---

## 6. The isolation chamber as a probe, not a theory

For this project, sensory deprivation is useful because it is approximately an **intervention on external drive**.

If the temporal structure of the current state really depends partly on closed body/brain loops, then reducing exteroceptive drive should reveal whether those endogenous coordinates retain causal leverage.

The conceptual experiment is:

```text
same internal loop
same recent perturbation

condition A: rich external input
condition B: weak external input

measure:
    internal-state decodability
    endogenous-noise amplification
    readout gain
    state persistence
    path dependence
```

Then separately allow adaptive gain or noncommuting state-dependent coupling.

The important comparison is not "sensory input versus no sensory input."
It is:

```text
input removal only
vs
input removal + readout reweighting
vs
input removal + homeostatic gain
vs
input removal + dynamic reconfiguration
```

That makes the isolation thought an actual systems-identification probe.

---

## 7. Current working conjecture

A possible bridge between the sensory-deprivation observations and the `PresentMoment` hypothesis is:

> **The experienced/current computational present may depend not only on which temporal traces exist, but on state-dependent gain that determines which traces currently have causal leverage.**

Then a "wide" or "thick" present is not simply more memory.

It is a changing causal support:

```text
trace exists
    !=
trace is currently readable
    !=
trace currently controls behavior
```

Danger, fatigue, quiet, sensory deprivation and neuromodulation could alter those relations without changing wall-clock time at all.

That is the next place to attack.
