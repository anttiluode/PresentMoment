# Independent collision: Misawa 2026 informational tuning

Date: 2026-08-12

A paper published only weeks before this note independently lands on almost exactly the
distinction that the PerceptionLab / KYY / PresentMoment controls forced us toward.

**Misawa K, Chinen K, Kawabata A, Kaiju T, Suzuki T, Komura Y. (2026). _Awake cortex
stabilizes traveling waves for global and reliable information routing._ iScience 29(8):
116728. DOI `10.1016/j.isci.2026.116728`, PMID `42472099`.**

This is important primarily as a **prior-art / convergence correction**, not something to
claim as support after the fact.

---

## 1. Their simulation is strikingly close to our carrier-aliasing guardrail

Misawa et al. explicitly start by showing that a traveling-wave-like temporal relation
does **not** guarantee directed information transfer.

Their Figure 2 compares two simulated conditions.

### Connected

```text
stimulus/noise -> X -> delayed Y
```

Y receives activity transmitted from X plus independent noise.

### Disconnected / common-drive-like control

```text
stimulus/noise -> X
same ERP-like input, delayed -> Y
```

Y is not causally driven by X.

The resulting evoked waveforms can be nearly identical in the two conditions, but
Transfer Entropy separates them: X->Y TE is significant only when the connection really
exists.

That is structurally the same identifiability problem independently encoded in

```text
experiments/frontier_mechanism_aliasing.py
```

where a sequential propagation chain and a common broadcast with graded receiver delays
produce identical passive lag profiles until an intervention separates them.

So the correction is now doubly clear:

> **A temporal frontier / traveling-wave appearance is not itself an information-routing
> claim.**

---

## 2. Their positive object is `informational tuning`

The authors then ask whether actual cortical information flow is geometrically related
to the current traveling-wave direction.

Using a large high-density ECoG array, for each seed electrode they compute Transfer
Entropy to surrounding electrodes and express TE magnitude as a function of angular
direction relative to the local wave-propagation direction.

Schematically:

```text
wave direction
      --->

seed o ----> neighbor       high TE?
     |\
     | \----> neighbor      lower TE?
     v
   neighbor
```

After rotating each local coordinate system so the wave points to angle zero, they obtain
an information-routing tuning curve.

They call the relation between neural-wave geometry and information-flow geometry
**informational tuning**.

The crucial conceptual step is:

```text
wave geometry
    != automatically
information-flow geometry

measure their alignment
```

That is extremely close to what `TEMPORAL_ACCESSIBILITY_OPERATOR.md` was trying to retain
with

```text
K_{receiver <- source}(t, lag, frequency | state)
```

except Misawa et al. already supply a concrete 2026 framework for one spatial-wave case.

---

## 3. Wakefulness changes the tuning, not merely the existence of waves

Their main biological result is also exactly the sort of distinction PresentMoment should
care about.

Visual-evoked waves exist in both awake and anesthetized states, but during wakefulness:

```text
wave propagation is more stable
wave motifs are more globally organized/diverse
information transfer is more reliably aligned with wave direction
```

Their Figure 5 reports TE-direction tuning around the wave direction, and the tuning is
sharper/more reliable in the awake condition than anesthesia.

So `state` changes the mapping

```text
wave / phase geometry
        ->
usable directed information flow
```

rather than simply adding or removing a wave.

That is a direct experimental example of a **state-dependent accessibility geometry**.

---

## 4. This removes novelty from the broad operator idea -- correctly

Do not claim as new:

```text
brain state changes directed information routing
wave direction can be compared with information-flow direction
waves do not guarantee causal information transfer
state can tune the alignment between the two
```

Misawa et al. have now done this explicitly for visual-evoked cortical waves and
wakefulness versus anesthesia, with code publicly released on Zenodo.

This is good news for the project in a different sense: the path reached independently
from a PerceptionLab accident is sitting on a live 2026 research frontier rather than in
an isolated metaphor.

---

## 5. KYY's null becomes more informative in this context

KYY's matched frontier controls found:

```text
forward maturity order ~= reverse maturity order
monotone maturity order ~= non-monotone contiguous blocks
```

and no generic advantage of temporal direction/order emerged.

Misawa's simulation likewise demonstrates:

```text
traveling-wave geometry alone does not imply directional information flow
```

These are different systems and should not be pooled statistically, but they reinforce
the same logical guardrail:

> **Direction must earn functional meaning from its relation to a readout / information
> pathway. Spatial-temporal order by itself is not semantics or routing.**

That fits KYY's older `READOUT_FIBERS.md` rule surprisingly well.

---

## 6. The narrower opening for PresentMoment

The broad visual-wave/wakefulness question is occupied.

The more specific question that remains interesting here is the one created by the
brain-body/time thread:

> **Does memory/arousal/interoceptive state reconfigure which temporally distributed
> sources are accessible to which receivers, and can that reconfiguration explain
> features attributed to a `wide present` better than a scalar duration window?**

A concrete human-memory version would combine two independently measurable objects:

```text
A. current wave / phase / slow-state geometry
B. directed hippocampus <-> cortical information transfer
```

and test whether A predicts changes in B beyond local power, task stage, electrode
distance and common-drive controls.

This is not `invent informational tuning again`.

It is a possible extension into episodic-memory and body-state regimes where the original
`PresentMoment` question lives.

---

## 7. New evidential ladder

For any future wave/frontier claim, require:

```text
LEVEL 0  geometry exists
         phase/lag/wave pattern is measurable

LEVEL 1  information exists
         receiver/source relation contains directed predictive information

LEVEL 2  geometry tunes information
         directed information is systematically related to the current wave/frontier

LEVEL 3  state tunes the tuning
         arousal/body/memory state changes that geometry-information relationship

LEVEL 4  behavior depends on it
         the tuning predicts or causally changes behavior beyond ordinary controls
```

PerceptionLab is a known-mechanism calibration around Level 0.

The first FR1 PTE work in this repo begins calibrating Level 1 for hippocampus-parietal
memory interaction.

Misawa et al. provide a real experimental Level-2/3 example for cortical visual routing
across wakefulness/anesthesia.

The open PresentMoment target is therefore not `find a wave`.  It is whether a comparable
state-dependent routing relation exists in the memory/body temporal systems that
motivated the project.

---

## Current sentence

> **A frontier is not yet a present, and a wave is not yet a route. The interesting
> variable is how the organism's current state tunes which temporal/spatial pathways are
> actually informative to their receivers.**

That sentence is now partly prior-art-informed rather than a novelty claim, which is
exactly how it should be.
