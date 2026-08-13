# Control-handle collisions — what is already known

## Status

This note exists to prevent `PresentMoment` / `PivotPoint` from renaming established
ideas and mistaking the rename for an invention.

The current synthesis contains at least four strong collisions.

---

## 1. Offline virtual machinery ↔ forward models / emulation theory

The provisional phrase `virtual machinery` was motivated by mental abacus, motor
imagery and learned tools:

> a learned external perception-action loop can sometimes be run partly internally
> when the external object/action is absent.

Rick Grush's 2004 **emulation theory of representation** already develops essentially
this class of mechanism from control theory: internal models of body/environment can be
driven in parallel with overt action and can also run offline for motor imagery,
visual imagery, action-outcome estimation and planning.

Primary reference:

- Grush, R. (2004), *The emulation theory of representation: Motor control, imagery,
  and perception*, Behavioral and Brain Sciences 27(3), 377–396,
  DOI `10.1017/S0140525X04000093`.

So:

```text
"run the missing body/world internally"
```

is not ours.

The abacus/person/tool branch is useful only if it yields a sharper measurable
constraint, such as:

```text
which learned transition structure transfers offline?
which parts remain subthreshold/output-suppressed?
which new callable trajectories appear through learning?
```

---

## 2. Several actions available now ↔ affordance competition

The PivotPoint intuition says that an organism does not have access to all physically
possible actions.  At a moment it has a smaller set of effective possibilities, and
context changes which one gains causal leverage.

Paul Cisek's 2007 **affordance competition hypothesis** already attacks the serial
picture of perception -> complete representation -> decision -> action.  It proposes
that sensory processing specifies several currently possible actions in parallel,
which compete while contextual/value information biases the competition.

Primary reference:

- Cisek, P. (2007), *Cortical mechanisms of action selection: the affordance
  competition hypothesis*, Philosophical Transactions B 362, 1585–1599,
  DOI `10.1098/rstb.2007.2054`.

So:

```text
potential actions coexist now and compete
```

is not ours either.

What `PresentMoment` can still ask is more temporal/receiver-relative:

```text
what unfinished work/signals/internal rollouts already constrain that competition?
what becomes readable next under each currently callable action?
```

---

## 3. Effective degrees of control ↔ empowerment

Claude suggested:

1. enumerate actions;
2. roll each forward;
3. cluster materially distinct futures;
4. count effective future branches rather than action labels.

This strongly collides with **empowerment**.

Klyubin, Polani & Nehaniv introduced empowerment as the information-theoretic capacity
of an agent's actuation channel: roughly, how much distinguishable influence an agent's
actions can exert on subsequently sensed states.

Primary reference:

- Klyubin, A. S., Polani, D. & Nehaniv, C. L. (2005), *Empowerment: A Universal
  Agent-Centric Measure of Control*, IEEE CEC 2005,
  DOI `10.1109/CEC.2005.1554676`.

A later overview states it explicitly as channel capacity between actions and sensors:

- Salge, Glackin & Polani (2014), *Empowerment — an Introduction*,
  arXiv `1310.1863`.

Our crude `effective control rank` is therefore not a new primitive.  In many settings
it should be compared directly against empowerment rather than invented as a competing
name.

This is a useful correction because empowerment already joins two things we care
about:

```text
controllability
       +
observability / what the agent can sense afterward
```

That is surprisingly close to `reachable accessibility`.

---

## 4. Callable learned handles ↔ chunks / options / motor primitives

The idea that a compact high-level command can launch a large learned sequence has
well-established relatives:

```text
motor primitives
motor chunks
hierarchical control
options / temporally extended actions in reinforcement learning
```

So `go home`, `reach`, `play this passage`, or `reconstruct the abacus` should not be
presented as a new kind of action abstraction.

The interesting question is narrower:

> how does learning change which temporally extended actions are **currently callable**
> from the control-potent surface, and therefore change the agent's empowerment /
> reachable-accessibility structure?

---

## 5. What might remain after subtraction

After naming the collisions, the current synthesis becomes smaller:

```text
                 maintained organism state
                          |
          processes / signals already in flight
                          |
              receiver-relative public state
                          |
          currently callable actions / emulators
                          |
        action-conditioned reachable/readable futures
                          |
             next control-potent surface
```

Most individual pieces are old.

The potentially useful conjunction is:

1. **unfinishedness is explicit** — some causes have started but their results do not
   exist yet; others exist but are travelling or unread;
2. **accessibility is receiver-relative** — physically present/decodable information is
   not automatically usable by the current controller;
3. **actions include learned internal trajectories** — imagery/retrieval/emulation can
   move internal state without overtly changing the corresponding external object;
4. **control is measured over distinct reachable/readable futures**, for which
   empowerment is a mandatory baseline;
5. **the control surface itself is state-dependent and can shrink/expand** with lesion,
   learning, fatigue, modulators and context.

Whether that conjunction buys anything is an empirical question.

---

## 6. A better definition than "degree of free will"

Do not measure nominal choice count.

For current local state `s`, receiver `r`, horizon `H`, and callable trajectories
`A(s)`, define the control question in established information-theoretic language:

```text
How much information can the choice among A(s)
transmit into receiver-relevant future state Y_r(t+H)?
```

Conceptually:

```text
E_r(s,H) = capacity[ A(s) -> Y_r(t+H) ]
```

This is a receiver-relative empowerment-like quantity.

It differs from generic empowerment only if the definition of `Y_r` is genuinely
restricted by the `PresentMoment` accessibility machinery rather than simply being a
renamed sensor vector.

That is exactly where comparison should happen.

### Kill condition

If ordinary empowerment on the full observable state predicts behavior/control as well
as the receiver-relative construction, remove the new vocabulary.

---

## 7. Relation to the subject

None of the collisions explains phenomenal subjectivity.

They do offer a much less mystical account of one functional component of
first-person-like organization:

```text
this organism has a small set of actions
whose consequences are evaluated
with respect to this organism's future observations and needs
```

A common origin is required for control even in a machine with no claim to phenomenal
experience.

Therefore:

> a control index can explain why behavior is perspectivally organized without
> explaining why there is something it is like to occupy that perspective.

Keep those questions separate.
