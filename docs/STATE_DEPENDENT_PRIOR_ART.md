# State-dependent recurrence: prior-art kill

The emerging `PresentMoment` discussion reached a structural observation:

> a fixed bank of exponential modes is reducible to a shared modal basis; state-dependent operators that do not commute can make path/order matter.

That observation is useful, but it is **not an unoccupied AI architecture idea**.

---

## 1. Mamba already makes part of the SSM selective

Gu & Dao, *Mamba: Linear-Time Sequence Modeling with Selective State Spaces* (2023/2024, arXiv:2312.00752) makes state-space parameters functions of the current input so that the model can selectively propagate or forget information.

In the standard Mamba formulation, the continuous `A` remains input-independent while `B`, `C` and the discretization step `Delta` are input-dependent.  Thus Mamba is directly relevant to the `B/C/gain` side of the current discussion even though it is not the full noncommuting `A(x)` case.

---

## 2. Bilinear RNNs occupy the stronger A(x) case

Ebrahimi & Memisevic, *Revisiting Bi-Linear State Transitions in Recurrent Neural Networks* (NeurIPS 2025), studies updates of the form

```text
h_t = A(x_t) h_(t-1)
```

where the transition matrix itself is generated from the current input through a bilinear interaction.

Most importantly for this project, the paper explicitly analyzes the expressive limitation that appears when the input-dependent transition matrices share a common eigenbasis: the resulting operations are commutative.  This is essentially the same algebraic distinction reached independently here.

Therefore:

```text
state-dependent A
+ noncommutativity
```

is not itself a novelty claim.

---

## 3. Closed-loop recurrent control is occupied too

Hu et al., *Improving Bilinear RNN with Closed-loop Control* (NeurIPS 2025), introduces Comba, a bilinear recurrent architecture with state-feedback and output-feedback corrections motivated explicitly by closed-loop control.

That is very close to the abstract systems form suggested by the brain-body loop discussion.

So we should not claim that "closing the recurrent loop" is an architectural invention either.

---

## 4. What survives for PresentMoment

The AI architecture ladder is therefore reduced:

```text
fixed exponential bank                 occupied
input-dependent B/C/gain               occupied (e.g. selective SSMs)
input-dependent transition A(x)        occupied (bilinear RNNs)
noncommuting state-dependent A(x)      occupied/analyzed
closed-loop state/output feedback      occupied
```

The surviving research question is biological/computational allocation:

> **Does the organism's peripheral physiological state participate in, or modulate, the effective state-dependent transition system that supports current temporal cognition?**

That is different from inventing a bilinear RNN.

Potentially testable consequences would have to involve constraints imported from actual body loops—measured delays, phases, gains, state-dependent coupling, perturbations or interoceptive feedback—not merely a generic learned `A(x)`.

---

## 5. Design rule

Do not build another generic state-dependent sequence model in this repository.

If an AI experiment is added, it must test a **body-loop-specific constraint** against strong controls such as Mamba/selective SSMs and bilinear recurrent models.

Otherwise `PresentMoment` has simply rediscovered current sequence-model research from physiology metaphors.
