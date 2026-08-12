# Geometric-Neuron / Deerskin injection into PresentMoment — audit state

Date: 2026-08-12

This note records the exact state after the ChatGPT delivery timeout so the thread is recoverable. Treat the old Geometric-Neuron / Deerskin material as hypothesis-generating noise, not as evidence.

## What was being audited

The useful residue of the old story was narrowed to:

- physical delay geometry;
- sampling/readout timing;
- band-specific spatial-mode persistence and switching;
- distributed reconstruction/readout rather than literal "hologram in a neuron";
- temporal accessibility: what source history is actually useful to a receiver after subtracting the history trivially implied by the signal's own spectrum/autocorrelation.

## Schizophrenia / RepOD audit

### Old headline metric does not survive

The old cross-band coupling result used dominant mode labels 0..5 and Pearson correlation of those integer labels. Mode labels are categorical, not metric; relabelling the same modes changes the statistic. The old code also scored a mode using square(mean(projected signal)) rather than mean(projected signal^2).

The literal current implementation did not reproduce the README headline HC~0.611 vs SZ~0.463, p=.007. Relabelling the same six modes could move nominal significance wildly, confirming the invariance failure.

### Repaired exploratory metric

A repaired version used:

1. real 10-20 electrode geometry;
2. graph Laplacian spatial modes;
3. actual projected mode energy (mean square);
4. label-invariant adjusted mutual information (AMI) across bands;
5. independent Fourier phase randomisation per channel as a spectrum/autocorrelation-preserving null.

On the initially chosen k=4 graph / 6-mode variant, SZ showed MORE cross-band spatial-mode dependence than HC, not less. The observed-minus-surrogate excess remained different between groups (roughly d~+0.98, p~.020). This is exploratory and was discovered after repairing the old metric.

### Robustness family completed

The stricter follow-up filtered each continuous EEG segment once before 0.5 s windows, discarded filter edges, and varied graph neighbourhood k in {3,4,5,6} and retained modes in {4,6,8}.

Result:

- SZ-HC sign was positive in 11/12 observed variants and 11/12 surrogate-subtracted variants;
- only 2/12 surrogate-subtracted variants had nominal p<.05;
- excess effect sizes ranged about -0.06 to +1.02;
- median excess p was ~.287.

Verdict: there is a sign-consistent hint, but not a robust biomarker. It should not be promoted until frozen and replicated independently. The earlier p~.02 result was parameter-sensitive.

## Schizophrenia topology / Takens audit

The old topology code described 10/20/40 ms delays but passed 10/20/40 as samples at 250 Hz, i.e. actually 40/80/160 ms. It also called a sum of H1 lifetimes a "Betti-1" count.

Using the stated 10/20/40 ms delays weakened the group difference. Counting H1 features rather than summing lifetimes weakened it further. Spectrum-preserving phase-randomised surrogates reproduced comparable group tendencies; observed-minus-surrogate group differences were not significant.

Verdict: no good evidence that the old schizophrenia topology result reflects nonlinear temporal geometry beyond ordinary spectral/autocorrelation structure.

## Alzheimer / Phi-Dwell audit

The five headline Alzheimer metrics (vocabulary size, entropy, mean dwell CV, top-5 concentration, Zipf alpha) are highly dependent summaries, not five independent converging markers. Rank-PCA put ~84% of their variance on one axis.

Five simple per-band self-transition rates explained a large fraction of the rank variance in all five metrics. After rank-controlling those switching rates, none of the five AD-vs-control headline differences remained significant in the committed result set.

A key algebraic simplification:

For a categorical sequence with N samples and self-transition fraction s,

    runs = N - s(N-1)
    mean_dwell = dt * N / runs

Since all subjects used the same N=5000, per-band mean dwell is exactly a monotonic transform of per-band self-transition rate. Therefore the reported "dwell gradient" is not an independent dynamical degree of freedom; it is a transformed summary of band-specific switching/persistence.

Verdict: the interesting surviving Alzheimer question is not "collapsed vocabulary / criticality / manifold" but whether disease changes band-specific persistence of physically meaningful spatial states beyond what ordinary spectral slowing predicts.

## First human-iEEG temporal-accessibility probe

A new estimator was deliberately made independent of PTE. For a frozen hippocampus <-> angular-gyrus pair in R1022J, target analytic-band state was predicted from fixed target self-history, then one source lag (10..640 ms) was added. Cross-validation held out whole trials. A condition-matched trial-mismatch null preserved each region's marginal spectrum/autocorrelation and event timing while breaking trial-specific pairing.

The mismatch-subtracted effects were tiny. There was no clean, consistent low-frequency-long-history versus beta-short-history result in this one pair. A few individual lags were nominal, but the profile did not justify a new biological claim.

Verdict: good negative gate. Do not infer a "deep low-frequency history horizon" from one subject. Freeze the estimator and test the already outcome-blind multi-subject FR1 cohort.

## Holographic / Pribram residue

Do not revive the literal claim that a neuron or soma stores a hologram. The useful modernizable residue is narrower:

- distributed representations can be reconstructed by a readout;
- readout is address/timing dependent;
- a compact event can recruit a larger distributed state over time;
- therefore "the present" may be better represented as a time-varying set of readable degrees of freedom than as a single fixed-width temporal container.

This is a framing, not a result.

## Next gates (frozen before looking)

1. **FR1 multi-subject lagged accessibility**: run the already-frozen six-subject anatomy-selected cohort with the same estimator and trial-mismatch null. Load-bearing quantities are subject-level mismatch-subtracted profiles, not raw low-frequency autocorrelation.
2. **Alzheimer raw-data persistence null**: go back to ds004504 and test only the primitive observable (per-band spatial-mode switching/self-transition), using phase-randomised and channel/trial nulls. Do not retest derived vocabulary metrics as if independent.
3. **RepOD independent replication**: freeze one repaired geometry definition before touching another schizophrenia dataset. Do not tune graph k or mode count on the replication set.
4. **Temporal accessibility language**: reserve 'history horizon' for excess recoverability after an appropriate marginal/spectral null. Slow bands having long autocorrelation by construction is not a finding.

## Current conceptual residue

After stripping away the broken pieces, the old repos inject one useful idea into PresentMoment:

> Time in a neural system may be less about a stored scalar age and more about which distributed states are readable, from where, at what phase/lag, and for how long their influence remains recoverable above the receiver's own dynamics.

Everything beyond that still has to earn itself experimentally.
