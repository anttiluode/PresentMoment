# Partial maturity, synchronization barriers, and the deadline gate

The starting observation is:

> A biological system does not have to finish every intermediate computation before consequences are allowed to propagate.

At one physical instant, one pathway can be carrying a coarse result, another can already have completed a useful sub-result, a third can still be integrating, and a fourth can be returning feedback from the body.

That suggests another way for a present state to be temporally thick:

> **different parts of the current state can have different computational maturities.**

This is related to, but distinct from, the earlier `SIGNALS_IN_FLIGHT.md` point.  A signal in flight stores recent causal history spatially.  Partial maturity asks whether downstream computation can *use* heterogeneous in-flight / partially refined state before a globally defined completion event.

---

## 1. Tighten the Transformer contrast

It is too strong to say that a Transformer cannot contain information of different semantic ages or qualities.

Residual connections can preserve relatively unchanged information while other features are transformed, and different tokens/features at the same layer can clearly represent very different things.

The precise architectural contrast is a **synchronization barrier**:

```text
standard layered execution

layer 0 tensor
    |
    v
[ complete block 1 ]
    |
    v
layer 1 tensor
    |
    v
[ complete block 2 ]
    |
    v
layer 2 tensor
```

In conventional execution, block `L+1` consumes a completed block-`L` representation.  At a given layer index, every position has undergone the same *count of block transitions*, even if its semantic content has not matured equally.

That uniform depth is part of what makes dense layer execution easy to batch and parallelize.

So do **not** claim:

> unfinished computation is mathematically impossible in a Transformer.

Claim only:

> **heterogeneous computational maturity is not the default scheduling semantics of a standard synchronized Transformer forward pass.**

---

## 2. The neuro/cognitive idea is old

The broad continuous-flow claim is established prior art.

McClelland's 1979 cascade model explicitly examined systems whose components operate continuously and pass information onward as it becomes available rather than waiting for a stage to finish:

- James L. McClelland (1979), *On the time relations of mental processes: An examination of systems of processes in cascade*, Psychological Review 86(4), 287-330. DOI: 10.1037/0033-295X.86.4.287

Eriksen & Schultz argued for a continuous-flow conception of visual processing in the same year:

- C. W. Eriksen & D. W. Schultz (1979), *Information processing in visual search: A continuous flow conception and experimental results*, Perception & Psychophysics 25, 249-263. DOI: 10.3758/BF03198804

Later macaque frontal-eye-field recordings found movement-related activity for distractors even when the ultimate saccade went correctly elsewhere, consistent with partial stimulus information reaching response-related circuitry before final selection:

- Murthy et al. (2001), *Continuous processing in macaque frontal cortex during visual search*, Neuropsychologia. PMID: 11516449.

This does not prove that all neural computation is continuous flow.  It does mean that "the brain can export partial results" is not a novelty claim.

---

## 3. Machine learning has also tried to buy partial computation

Several neighboring ML families already attack variable / interruptible computation.

### Adaptive computation / halting

- Graves (2016), *Adaptive Computation Time for Recurrent Neural Networks*, arXiv:1603.08983.
- Universal Transformers (Dehghani et al., 2018), arXiv:1807.03819, combine recurrent depth with a per-position dynamic halting mechanism.
- PonderNet (Banino et al., 2021), arXiv:2107.05407, learns how many computational steps to use.

### Dynamic Transformer depth

Mixture-of-Depths dynamically routes which token positions participate in attention/MLP computation at particular layers:

- Raposo et al. (2024), *Mixture-of-Depths: Dynamically allocating compute in transformer-based language models*, arXiv:2404.02258.

This weakens any claim that all Transformer tokens must always receive identical useful compute.

### Early exit / anytime prediction

Early-exit networks attach predictions to intermediate layers.  An important negative result is that ordinary early exits are not automatically good anytime predictors: on individual examples, prediction quality need not improve monotonically with additional computation.

- Jazbec et al. (NeurIPS 2023), *Towards Anytime Classification in Early-Exit Architectures by Enforcing Conditional Monotonicity*.

So "answer whenever the deadline hits" is already a field, not a new benchmark concept.

### Asynchronous/event-driven neural computation

The closest prior art to the current seam explicitly removes layer synchronization.

Koopman et al. study asynchronous spiking execution and report that simply removing synchronization from synchronously trained networks can break their dynamics.  Their asynchronous-aware training can reduce spike use and latency while retaining or improving accuracy:

- Koopman et al. (TMLR 2025), *Exploring / Overcoming the Limitations of Layer Synchronization in Spiking Neural Networks*, arXiv:2408.05098.

Other relevant systems include:

- Schaefer, Gehrig & Scaramuzza (2022), *AEGNN: Asynchronous Event-based Graph Neural Networks*, arXiv:2203.17149.
- Turrero et al. (ICML 2024), *ALERT-Transformer*, which continuously integrates asynchronous events into an always-up-to-date representation that can be sampled at arbitrary rates.

Therefore:

> **asynchrony, anytime prediction, partial computation and removing layer barriers are all occupied.**

---

## 4. What remains interesting for this project

The narrower physical claim is different:

> In a local delay substrate, mixed computational maturity is not a controller decision.  It is the ordinary physical state of the machine.

A packet on a fast route may already have reached a useful downstream state while another packet is still propagating through a slower route.

There is no universal event called:

```text
EVERYTHING AT DEPTH 7 IS FINISHED
```

unless the implementation deliberately inserts one.

That makes the candidate advantage a **cost / robustness / inductive-bias** question, not an expressivity claim.

A Transformer + early exits can emulate useful early answers.
An ACT/Ponder system can learn when to stop.
An asynchronous SNN can remove barriers explicitly.

The possible local-delay advantage would have to be something like:

> **good deadline behavior emerges from the substrate without a separate halting/router/exit policy and survives deadlines or delay patterns not used during training.**

That is testable.

---

## 5. A useful state variable: computational maturity

For a local node/branch `v`, define a descriptive maturity coordinate

```text
m_v(t) = amount / number of causal refinement operations that have reached v by physical time t
```

This is not claimed as new mathematics.

A synchronized layered system approximately constrains

```text
m_1(t) = m_2(t) = ... = m_N(t)
```

between barriers.

A heterogeneous delay fabric allows

```text
m_1(t) != m_2(t) != ... != m_N(t)
```

as its normal state.

The present can therefore contain a **maturity field** as well as an activation field.

Useful diagnostics for later experiments include:

```text
mean maturity
variance of maturity across nodes
which mature states currently influence the readout
time until each local state becomes causally legible
```

The key point is that `m_v(t)` is indexed by *physical time*, not merely layer number.

---

## 6. Gate 0: same computation, different scheduling

`experiments/deadline_partial_maturity.py` isolates only this scheduling property.

Twelve branches refine noisy evidence through five stages.  Local step delays are heterogeneous.

Two schedules receive **exactly the same**:

```text
branch evidence
per-stage estimates
local step delays
final sum readout
```

Only scheduling changes.

### ASYNC

Each branch starts its next stage as soon as its own previous stage completes.
At a deadline, branches can sit at different refinement depths.

### SYNC + early exit

Every branch waits for the slowest branch at each layer before the next layer begins.

To make this a strong control, the synchronized system is allowed a readable early-exit prediction after **every** completed barrier.  No learned halting controller is required.

Thus this gate is not:

```text
async can answer early
vs
sync is forbidden to answer early
```

It is:

```text
heterogeneous local progress
vs
barrier-synchronized progress
```

---

## 7. Gate-0 result

Default run:

```bash
python experiments/deadline_partial_maturity.py
```

Ten random delay fabrics x 10,000 episodes each.

### Neutral evidence

| deadline / full sync latency | async accuracy | sync + exit accuracy | mean async depth | mean sync depth |
|---:|---:|---:|---:|---:|
| 0.00 | .500 | .500 | 0.000 | 0.000 |
| 0.10 | .745 | .500 | .733 | 0.000 |
| 0.20 | .868 | .725 | 1.967 | .700 |
| 0.25 | .892 | .756 | 2.408 | .800 |
| 0.35 | .939 | .854 | 3.517 | 1.500 |
| 0.50 | .964 | .904 | 4.625 | 2.300 |
| 0.75 | .969 | .942 | 4.958 | 3.200 |
| 1.00 | .969 | .969 | 5.000 | 5.000 |

Deadline-area accuracy:

```text
async              0.9042
sync + early exit  0.8303
```

The equality at the final deadline matters: both schedules perform the same final computation and converge to the same answer distribution.

Before the deadline, the asynchronous version can expose refinements from fast branches without waiting for unrelated stragglers.

### Fast-channel conflict

The stress condition deliberately makes some fast branches misleading in 35% of episodes and gives slower branches corrective evidence.

Deadline-area accuracy:

```text
async              0.8664
sync + early exit  0.7979
```

At the 10% deadline, about 27.5% of episodes are wrong under the asynchronous readout but become correct by the final computation; only about 2.3% go from correct to wrong.

This is intentionally constructed, so it is **not** evidence for a human illusion.

It merely demonstrates the cost side:

> making partial computation legible also makes premature computation legible.

---

## 8. Why Gate 0 is not a result yet

The experiment is structurally biased toward asynchronous scheduling before the final barrier.  That is what it was built to expose.

It therefore establishes only:

> **with heterogeneous local delays, removing global barriers creates a smoother and earlier availability curve for exactly the same staged computation.**

That is nearly definitional.

It does **not** establish:

- that a local delay mesh learns better representations;
- that it beats an anytime Transformer;
- that it uses less hardware energy;
- that its early predictions are better calibrated;
- that brain computation works this way everywhere;
- that human temporal illusions fall out of the mechanism.

The next gate has to earn those.

---

## 9. Gate 1: put delays into the actual local machine

The natural next object is KYY's local-scattering line, because that project already has the correct strong algebraic controls.

Do not invent another generic delay reservoir.

Instead compare an actual local operator under different scheduling semantics:

```text
A. KYY/local operator, globally synchronized steps
B. same operator + fixed heterogeneous local edge delays
C. same operator + edge delays + asynchronous event scheduling
D. synchronized model + early-exit heads
E. strong recurrent / selective-state baseline
F. asynchronous/event-driven baseline where practical
```

Important constraints:

1. Same information.
2. Same local operators where A/B/C are compared.
3. Count actual operations/messages, not nominal layers only.
4. Read at externally imposed deadlines.
5. Do not train a special halting controller for the async model.
6. Train on one deadline distribution and test on unseen deadlines.
7. Warp edge delays OOD after training.

Report:

```text
accuracy vs physical deadline
area under accuracy-deadline curve
calibration vs deadline
wrong-early -> right-late corrections
right-early -> wrong-late regressions
operations/messages consumed by deadline
state size
sensitivity to a slow/failed edge
```

The strongest possible test is:

> train primarily for the final answer, then interrupt the machine at deadlines it never saw during training.

If good intermediate behavior appears anyway, the substrate has bought something interesting.

If an early-exit / asynchronous baseline matches it with equal machinery and compute, the special claim dies.

---

## 10. Connection back to PresentMoment

The current project now has several distinct ways that an instantaneous state can contain temporal structure:

```text
fading modes              past events remain as current residue
signals in flight         recent source times coexist spatially
body/world feedback       old actions are still changing future input
cyclic phase              heartbeat / respiration mark recurrent coordinates
partial maturity          current subcomputations have heterogeneous causal depth
```

These should not be conflated.

The new candidate sentence is:

> **A biologically thick now may contain not only different ages of evidence, but different ages of computation.**

That is much closer to the original intuition that the brain does not freeze a complete matrix, finish it, and then advance the universe by one block.

But this repository should keep the claim operational:

> **Does heterogeneous physical-time maturity provide useful, robust deadline behavior once strong anytime and asynchronous controls are included?**

That is the gate.
