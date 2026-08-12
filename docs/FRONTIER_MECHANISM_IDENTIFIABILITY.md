# Frontier mechanism identifiability: lag is not a carrier

Date: 2026-08-12

This is a guardrail produced by the PerceptionLab wave calibration and the 2026 human
infra-slow-wave literature.

## The problem

A spatial lag profile can be real and reproducible without identifying the mechanism that
created it.

The PerceptionLab Wave Field has a known generative law: a perturbation propagates through
a second-order field.  Its probe lags therefore really are travel-time lags **inside that
toy**.

For biology, the mechanism is not supplied to us.

`experiments/frontier_mechanism_aliasing.py` constructs two systems with the same input
and identical receiver observations.

### Mechanism A: sequential propagation

```text
source -> R0 -> R1 -> R2 -> R3
```

Using edge delays

```text
2, 3, 4, 5
```

gives cumulative receiver delays

```text
2, 5, 9, 14
```

### Mechanism B: common broadcast + receiver delays

```text
             -> R0 delay 2
source ------> R1 delay 5
             -> R2 delay 9
             -> R3 delay 14
```

For passive observation both implement

```text
y_i(t) = u(t - d_i)
```

and therefore produce exactly identical traces and pairwise lags.

The GitHub Actions known-answer gate verified this equality.

Pairwise lags were

```text
(0,1)  3
(0,2)  7
(0,3) 12
(1,2)  4
(1,3)  9
(2,3)  5
```

for both mechanisms.

## Intervention separates them

Cut the sequential path after R1.

Then the propagation mechanism gives

```text
R0 peak 5
R1 peak 8
R2 absent
R3 absent
```

whereas the common broadcast still gives

```text
R0 peak 5
R1 peak 8
R2 peak 12
R3 peak 17
```

So the mechanisms are distinguishable under intervention even though they are aliased
under passive timing.

## Why this matters for current brain work

Yang et al. (Nature Communications 2026,
DOI `10.1038/s41467-026-69068-x`) report human infra-slow SM-to-DMN fMRI waves coordinated
with sensory encoding and memory retrieval.  Their discussion explicitly warns against
a simple corticocortical-conduction interpretation because the seconds-scale apparent
propagation is too slow for ordinary axonal travel.

They propose that broad neuromodulatory/subcortical broadcast could act on neuronal
groups with systematically different delay/composition across regions, translating into
an apparent spatial fMRI wave.

That is structurally close to the aliasing control above.

Therefore the correct cross-repo statement is:

> **PerceptionLab calibrated an effective temporal frontier and a lag instrument.  It did
> not license the inference that a similar measured frontier in brain data is carried by
> the same propagation mechanism.**

## Measurement hierarchy

Keep these levels separate:

```text
1. OBSERVED FRONTIER
   reproducible lag / phase / activation ordering across receivers

2. FUNCTIONAL FRONTIER
   changing that ordering changes what receivers can decode/do

3. CARRIER MECHANISM
   local propagation, shared drive, neuromodulation, oscillatory phase organization,
   recurrent interaction, vascular/hemodynamic effects, or combinations
```

Level 1 does not establish level 3.

Level 2 is stronger but can still leave multiple carriers compatible with the data.

Carrier claims require interventions, multiscale recordings, anatomical constraints or
other system-identification evidence capable of separating competing mechanisms.

## Consequence for `causal-age surface`

The phrase remains useful as an observational shorthand but should not imply literal
packets travelling between every measured receiver.

Prefer:

```text
effective temporal frontier
receiver-maturity surface
retarded-time profile
```

when the carrier is unknown.

## Stop rule

Do not build a more realistic wave PDE in PresentMoment merely because brain data show a
wave-like lag gradient.

First ask what alternative common-drive / graded-response mechanism produces the same
observable.  If passive data cannot distinguish them, the next experiment should be an
intervention or an additional measurement—not a prettier propagation simulation.
