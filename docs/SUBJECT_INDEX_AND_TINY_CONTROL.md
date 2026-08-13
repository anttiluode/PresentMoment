# Subject index and tiny control

## Status

Working decomposition.  This note does **not** explain phenomenal consciousness.
It separates an unsolved question from a more experimentally tractable one.

The two starting questions are:

```text
Why is there a subject at all?

How does that subject/system acquire tiny degrees of control over the gigantic
machine it inhabits?
```

The first sentence currently hides several different explananda.

---

## 1. Split the subject problem before trying to solve it

At least four questions should be kept distinct.

### A. Phenomenal subjectivity

Why is any physical/information-processing state experienced at all?

`PresentMoment` has no answer.  A control architecture, a thalamocortical loop, a
workspace, an egocentric map or a PivotPoint does not close this explanatory gap by
being renamed consciousness.

### B. Subject index / perspectival organization

Why are representations so often organized around something like:

```text
here
this body
this effector
this need
what happens if I do X?
```

This is empirically approachable.

### C. Unity / continuity

What keeps a subject/process continuous while language, memory, vision,
metacognition, bodily-self variables or motor report can fail selectively?

This is the `SELF_BY_SUBTRACTION.md` problem.

### D. Control bottleneck

How can a very small set of currently available decisions influence a vastly larger
organism whose implementation is mostly inaccessible to introspection?

This is the `VIRTUAL_MACHINERY_AND_CONTROL_HANDLES.md` problem.

Do not use evidence for B, C or D as if it solved A.

---

## 2. Candidate functional object: the control index

A control system must evaluate futures relative to the thing being controlled.

A useful schematic is:

```text
world / body state
       |
       v
state relative to this body / effector / need
       |
       +---- action a1 ---> predicted future of this organism
       +---- action a2 ---> predicted future of this organism
       +---- action a3 ---> predicted future of this organism
```

Call the common reference, provisionally, the **control index**.

It is not an anatomical point and not necessarily a single neural representation.
It is the shared origin with respect to which action-conditioned consequences become
comparable.

This is deliberately weaker than saying "the self is a control model."

The proposal is only:

> **perspectival organization may be partly forced by control: useful counterfactuals
> have to be indexed to the body, effectors, needs and future states of the organism
> that can actually act.**

---

## 3. Existing science already owns much of this territory

### Egocentric value maps

Bufacchi et al. (Nature Neuroscience, 2025, DOI
`10.1038/s41593-025-01958-7`) model body-part-centered peripersonal fields as action
value rather than mere spatial coordinates.  Collections of such fields form an
**egocentric value map** of the near-body environment.

This is important because the map is not simply:

```text
where is object X?
```

but closer to:

```text
what does X afford / threaten relative to this body part and action repertoire?
```

That is already a small scientific version of a control-indexed world.

### Hippocampal compositional maps and replay

Bakermans et al. (Nature Neuroscience, 2025, DOI
`10.1038/s41593-025-01908-3`) show how compositional state-space building blocks and
hippocampal replay can construct memories that immediately imply useful future
behavior.  Their framework explicitly links relational representations to policies and
shows how replay can build representations at locations not physically visited after a
new landmark is discovered.

This supports a precise form of "the absent world can continue to compute": learned
relational dynamics can be recomposed and replayed offline.

It does not imply that replay is conscious imagination.

### Action plans and their outcomes

Barnaveli et al. (Nature Communications, 2025, DOI
`10.1038/s41467-025-59153-y`) report hippocampal-entorhinal and cortical motor
representations related to action plans and outcomes.

Again, this is compatible with action-conditioned future structure without locating a
subject in hippocampus.

---

## 4. Virtual machinery plus output-null dynamics gives a stronger mechanism

The mental-abacus example suggests more than static memory retrieval.

A learned physical loop can be approximated internally:

```text
physical tool state
 -> see / feel
 -> act
 -> changed tool state
 -> see / feel
 -> ...
```

After training:

```text
internalized tool state
 -> predicted sensory state
 -> covert action update
 -> predicted next state
 -> ...
```

But why does imagining the action not simply execute it?

`PUBLIC_AND_PRIVATE_SUBSPACES.md` already supplies a candidate systems answer:
ongoing computation can occupy **output-null/private** dimensions while only a small
projection is output-potent.

So the combined picture is:

```text
invoke learned machine
       |
       v
reinstantiate a partial sensory / motor transition system
       |
       v
keep much of the trajectory output-null
       |
       +--> expose selected intermediate information to other internal receivers
       |
       +--> expose a small final consequence to speech / hand / eye / next thought
```

This makes imagery more interesting than "weak execution."

The hidden machine may retain transition structure while its normal physical output
channel is suppressed or redirected.

That is testable.

---

## 5. Tiny control through learned handles

The high-level control surface does not need direct access to all lower-level state.

A handle can be tiny:

```text
reach
stand up
say this sentence
retrieve the abacus
walk home
play the song
go for a ride
```

while the launched machinery is huge.

This suggests a functional compression:

```text
millions of low-level state variables
             |
          learning
             v
small repertoire of reliable callable trajectories
```

The handle does not have to contain its implementation.

This is close to established ideas from motor primitives, action chunking and
hierarchical reinforcement learning.  `PresentMoment` should not claim to have invented
those concepts.

The potentially useful synthesis is the link to the current causal present:

> **the organism's effective degrees of control are the learned trajectories that are
> currently callable from the control-potent surface, not all physically possible
> microscopic state changes.**

---

## 6. Effective control degrees of freedom

Claude's earlier suggestion can now be made operational.

At a current state `s`, let the available high-level handles be:

```text
A(s) = {a1, a2, ..., ak}
```

For each handle, estimate a distribution over relevant future states after horizon H:

```text
P(S_H | s, ai)
```

Do **not** count action labels.

Two actions are effectively the same degree of freedom if their reachable futures are
not materially distinguishable for the organism/task.

A crude empirical procedure is:

1. roll each available action/handle forward;
2. represent its future-state distribution;
3. cluster futures by task-relevant distance;
4. count/rank materially distinct clusters;
5. repeat under learning, fatigue, neuromodulation, lesion, stress, context or tool use.

This produces an **effective control rank** rather than a nominal action count.

### Important prediction

Skill learning can increase effective control rank without adding new muscles or
sensors.

The new degree of freedom is a newly reliable trajectory through existing machinery.

Conversely, transient dysfunction can collapse control rank while leaving the subject
present.

---

## 7. The subject as origin of counterfactuals — candidate, not conclusion

A more provocative formulation now becomes possible:

> perhaps one empirically accessible component of "me" is the common reference with
> respect to which counterfactual futures are evaluated: **if I do X, what happens to
> this organism next?**

This would make the subject-index less like a stored object and more like an origin in
a family of action-conditioned trajectories.

Schematically:

```text
                     future 1
                   /
current organism -- future 2
                   \
                     future 3

         ^
         |
   common control index
```

This is **not** an account of why those trajectories are experienced.

It is a candidate account of why cognition has a first-person-shaped reference frame
and why that reference is useful for control.

---

## 8. Tool incorporation gives a clean prediction

Tool use is useful because it can change the effective actionable boundary without
moving the biological subject.

Classic macaque work (Iriki et al., 1996, DOI
`10.1097/00001756-199610020-00010`) showed tool-use-dependent expansion of
body-part-centered receptive fields.

The 2025 egocentric-value-map framework makes a related computational prediction:
peripersonal fields should depend on action repertoire/value, not only metric distance.

So under training:

```text
before tool mastery:
    object beyond hand = weakly reachable

after tool mastery:
    same object + rake = part of a reliable reachable trajectory
```

The interesting variable is not whether the rake becomes literally "self."

It is whether the **reachable-future geometry** and egocentric value field change.

That is measurable.

---

## 9. Absent people fit only after a warning label

An absent person can also leave learned transition structure:

```text
if I say X, they often say Y
this topic changes my state in direction Z
this person's imagined judgment suppresses action A
this memory makes action B more likely
```

Social-map work supports structured relational representations of other people.  That
does not make another person a detachable module or prove that we run a full simulation
of them.

The useful hypothesis is narrower:

> **some social memories are callable predictive machines whose reinstatement changes
> the current reachable-future landscape.**

A strong test would need trajectory prediction, not merely semantic similarity or
activation during person recall.

---

## 10. Experimental ladder

### Gate 1 — execution versus imagery

Current experiment: PhysioNet EEGMMIDB cross-condition transfer with sensorimotor versus
occipital control (`experiments/eegmmidb_virtual_machinery.py`).

Question: does task-relevant left/right geometry survive when movement becomes covert?

### Gate 2 — verify output-nullness with EMG

A stronger 2026 public dataset contains 60-channel EEG plus EOG and EMG during actual
and imagined sit-to-stand / stand-to-sit transitions (Leelakittisin et al., GigaScience
2026, DOI `10.1093/gigascience/giag065`).

This is attractive because EMG can test whether an imagery trial really lacks the
ordinary muscular output while EEG still carries transition-related structure.

Useful test:

```text
shared EEG transition geometry
         +
no corresponding execution-like EMG
```

That would be much closer to an **output-null virtual machine**.

### Gate 3 — learning creates a new handle

Use longitudinal skill-learning data (mental abacus, motor sequence learning, tool use)
to ask whether training increases the number/separability/reliability of reachable
future trajectories from a compact cue.

### Gate 4 — lesion removes the handle but not the subject

The mental-abacus stroke case is a natural example.  Build a wider lesion table for
selective loss of learned skills/imagery and ask whether the corresponding effective
control rank collapses while general consciousness persists.

---

## 11. Falsifiers

We should weaken this synthesis if:

- execution-to-imagery similarity disappears under cue-matched controls;
- EMG reveals that supposed imagery effects are simply covert movement;
- learned "handles" do not compress behavior or change reachable-future structure;
- tool/body-centered effects are explained entirely by sensory attention rather than
  action value/repertoire;
- social reinstatement predicts no dynamics beyond ordinary semantic association;
- the proposed control index adds no predictive power over standard egocentric/action
  value models.

And even if every gate succeeds:

```text
functional subject-index
    !=
phenomenal subjectivity explained
```

That boundary must remain explicit.

---

## 12. Current working synthesis

The strongest current sentence is:

> **Learning can turn interactions with the world into callable internal transition
> systems.  A small current control surface can invoke those systems while keeping much
> of their dynamics output-null, thereby gaining leverage over a vast organism through
> a limited set of learned handles.  A persistent agent-relative control index may
> organize those handles and their predicted consequences, but none of this yet
> explains why the process is experienced by a subject.**
