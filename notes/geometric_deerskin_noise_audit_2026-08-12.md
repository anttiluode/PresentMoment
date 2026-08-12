# Geometric-Neuron / Deerskin noise injection — 2026-08-12

These repositories were reintroduced as **hypothesis-generating noise, not gospel** while PresentMoment was studying temporal accessibility in brain dynamics. The point of this pass was to retain only claims that survived invariance, surrogate, and independent-data checks.

## 1. What survived conceptually from the newer Deerskin/Fable audit

The useful corrected residue is narrow:

- delay / cable dynamics can carry an arrow;
- static amplitude or a common-drive spatial skin cannot by itself establish direction;
- sampling/readout timing matters;
- Fourier / I-Q multiplexing is real mathematics, but observer bookkeeping must not be mistaken for physical memory;
- spatial geometry can be a useful projection/readout basis without implying a literal holographic soma.

This is compatible with PresentMoment's independently reached guardrail: **frontier != carrier**. A lag surface or apparent traveling wave does not identify the mechanism that generated it.

## 2. RepOD schizophrenia: the original cross-band coupling claim did not survive

The old Geometric-Neuron headline was roughly HC 0.611 vs SZ 0.463, p=.007, interpreted as reduced cross-band eigenmode coupling in schizophrenia.

The current code has several load-bearing problems:

1. the graph is a ring in EDF/channel order, not physical 10-20 geometry;
2. each 0.5-s word is separately bandpass filtered;
3. "mode power" is `(temporal mean projection)^2`, not mean squared projected energy;
4. dominant mode identities 0..5 are categorical but Pearson-correlated as if their integer labels had meaningful distances;
5. arbitrary global mode relabeling therefore changes the result.

Running the literal current implementation on public RepOD did **not** reproduce the headline: HC=0.0092, SZ=0.0324, p=.102, with the sign reversed.

An exact 6! = 720 relabeling audit preserved every dominant-mode trajectory and changed only the arbitrary names 0..5. The resulting p-values ranged from .014 to .988; only 13.3% were nominally <.05. The measure is not label invariant.

Replacing squared-mean projection with actual mean squared mode energy removed the ring effect.

## 3. RepOD topology result also failed its intended interpretation

The paper text describes Takens delays 10/20/40 ms. The code passes `(10,20,40)` as sample indices at 250 Hz, hence it actually uses 40/80/160 ms.

The function called `compute_betti1` does not return a Betti-1 count. It thresholds H1 feature lifetimes and sums them, i.e. a form of H1 total persistence.

Audit results, paper exclusion set n=26:

- code-scale 40/80/160 ms total persistence: HC=16.88, SZ=15.22, p=.080;
- true 10/20/40 ms total persistence: HC=13.53, SZ=12.71, p=.300;
- actual surviving H1 feature count at true delays: p=.614.

Fourier-phase-randomized signals that preserve each subject's spectrum/autocorrelation already produced a comparable HC/SZ tendency. Subject-level observed-minus-surrogate differences were not significant (code scale p=.273; true-ms scale p=.128).

Conclusion: this analysis does not provide evidence for a schizophrenia-specific nonlinear/topological manifold effect beyond ordinary spectral/autocorrelation structure.

## 4. A repaired spatial-energy metric looked interesting in RepOD, then failed independently

A deliberately repaired exploratory observable used:

- real standard 10-20 electrode geometry;
- graph Laplacian modes;
- actual projected mode energy;
- label-invariant adjusted mutual information (AMI) between band-specific dominant-mode sequences;
- independent per-channel Fourier phase randomization as a spectrum/autocorrelation-preserving null.

On RepOD, the first repaired version gave:

- observed AMI HC=0.00351, SZ=0.01739, p=.0165, d(SZ-HC)=+1.01;
- surrogate group effect p=.633;
- observed-minus-surrogate excess HC=0.00066, SZ=0.01336, p=.0198, d=+0.98.

This was the **opposite direction** from the old README: SZ showed more, not less, cross-frequency dependence of spatial-mode energy.

A harsher continuous-filter robustness family varied physical graph neighborhood k={3,4,5,6} and retained modes={4,6,8}. The SZ>HC sign persisted in 11/12 variants, but only 2/12 excess effects had nominal p<.05. The frozen k=4 / 6-mode version fell to d=+0.726, p=.0765. Median excess p across variants was .287. Thus RepOD was directionally suggestive but statistically fragile.

### Independent gate: OpenNeuro ds003944 first-episode psychosis

Before inspecting any ds003944 outcome with this metric, the following were frozen:

- first 12 lexicographic Control and first 12 lexicographic Psychosis subjects;
- canonical 19 electrodes shared with RepOD;
- continuous filtering;
- physical 4-neighbor graph;
- 6 modes;
- 0.5-s energy winner;
- cross-band AMI;
- observed minus independent-channel Fourier-phase-surrogate excess.

Frozen prediction: **Psychosis excess AMI > Control excess AMI**.

Result:

- Control mean excess AMI = 0.0919646
- Psychosis mean excess AMI = 0.0458074
- Psychosis - Control = -0.0461572
- Cohen d = -0.497
- two-sided t p = .236
- preregistered one-sided p for the predicted positive sign = .882
- Mann-Whitney two-sided p = .436
- predicted sign observed = **false**

The sign reversed. Per the precommitted gate, **do not enlarge the cohort or retune the metric**. The repaired RepOD finding is best treated as a post-hoc dataset-specific curiosity, not current evidence for a psychosis-spectrum spatial-mode biomarker.

## 5. Alzheimer Phi-Dwell: five headline markers collapse mostly onto switching/persistence

The Alzheimer analysis at least used physical 10-20 geometry. However, the five advertised markers are highly dependent summaries of the same token dynamics.

Across the committed 88-subject result set:

- vocab vs entropy Spearman rho=.975;
- top-5 concentration vs Zipf rho=.956;
- first rank-PCA component explains 84.2% of the five headline metrics.

Raw AD-vs-CN p-values for vocab, entropy, mean CV, top-5 concentration, and Zipf were all about .010-.021.

But the five simple per-band self-transition rates explain roughly 49-75% of rank variance in those headline markers. After rank-controlling the five band self-transition rates, none of the five AD-vs-CN differences remained significant (p=.114-.756).

There is also an exact algebraic redundancy. For a categorical mode sequence of length N with self-transition fraction s,

`number_of_runs = N - s(N-1)`

and therefore

`mean_dwell = dt * N / [N - s(N-1)]`.

All stored subjects have N=5000 words. Thus band mean dwell is a deterministic transform of band self-transition rate. The reported `dwell_gradient` is not an independent dynamical degree of freedom; it is a transformed summary of how band-specific mode-switching rates vary with frequency.

The disease signal may still live in those switching rates. What is not earned is the stronger vocabulary of five independent biomarkers, collapsed manifold, or criticality. In particular, CV>1 of dwell-run lengths is overdispersion; it does not by itself establish neural criticality.

## 6. The direct 'causal history horizon' bridge to PresentMoment failed

A separate human FR1 iEEG gate asked whether different frequency routes expose different depths of trial-specific source history.

Frozen R1022J pair:

- hippocampus DG/CA1 bipolar LB2-LB3;
- left angular gyrus LH11-LH12.

Estimator was deliberately independent of PTE: cross-validated ridge prediction of target analytic state from fixed target self-history, with one source lag (10..640 ms) added. Source trials were mismatched within condition as a null preserving each region's marginal spectrum/autocorrelation and event timing while breaking trial-specific pairing.

After mismatch subtraction, directional delta-R2 differences were microscopic (~1e-6), with no coherent delta/theta long-history advantage. Successful encoding had no nominal positive lag in either direction; recall had one isolated parietal->hippocampal point at 320 ms. Beta likewise had isolated points but no stable profile.

Per the gate, this branch stops. Frequency-multiplexed routing does **not** automatically imply different recoverable depths of causal history.

## 7. Holographic / Pribram noise after stripping the metaphor

The literal claim "the neuron/brain is a hologram" is not needed and was not established here.

The useful residue is **address-dependent distributed reconstruction**:

- representations can be distributed over spatial/spectral coordinates;
- a compact trigger does not need to contain a literal picture;
- what becomes readable can depend strongly on when and where the system is sampled;
- observer-supplied addresses must not be confused with physical memory.

Recent human iEEG work fits this stripped version better than the old holographic language: successful retrieval can begin with a hippocampal ripple and be followed hundreds of milliseconds later by expanded cortical representational dimensionality/reinstatement; closed-loop stimulation timed to hippocampal theta phase changes network responses compared with phase-blind stimulation.

A useful conceptual shift for PresentMoment is therefore:

> Memory may not be a wide stored strip of past time. **Access itself can unfold.**

The current moment may be better thought of as a temporally evolving set of readable / potent degrees of freedom than as a scalar-duration container.

## 8. What the noise actually contributed

The old repositories did not rescue a scalar "wide present" theory. Most of their strongest disease interpretations became smaller under audit.

What remains worth carrying forward is simpler:

1. **physical delay / skew can create direction; static geometry cannot;**
2. **sampling/readout timing matters;**
3. **spatial modes provide a useful coordinate system only when geometry is physical and statistics are label invariant;**
4. **band-specific persistence/switching is a real temporal observable;**
5. **distributed reconstruction can unfold after a trigger, so accessibility can change over time without storing a literal temporal frame;**
6. **every temporal/directional metric needs a null preserving the marginal spectrum/autocorrelation, because those alone can manufacture impressive-looking structure.**

This leaves PresentMoment with a less romantic but stronger question:

> At a given physiological state, which spatial/spectral degrees of freedom are currently readable or potent at each receiver, and how does that accessible set reconfigure over time?

That is closer to an evolving observability/accessibility geometry than to a width of 'now'.
