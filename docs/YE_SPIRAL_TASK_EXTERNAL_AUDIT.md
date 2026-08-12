# External audit: Ye spiral-wave task data pushed back

Date: 2026-08-12

This note is intentionally different from the earlier conceptual notes in this repository.
It records contact with another lab's public data and code where the answers were not
chosen by this project.

Source project:

- Ye et al., *Brain-wide topographic coordination of traveling spiral waves*
- public companion code: `zhiwen10/YE-et-al-2023-spirals`
- public Figshare visual-motor task deposit: article `27850542`, one ~14.2 GiB `task.zip`

The authors' public repository is newer than the supplied preprint and includes whisker
and visual-motor task analyses. HTTP ZIP-range reads were used in GitHub Actions to
inspect/extract only needed processed files rather than download the full archive.

The motivating question was deliberately simple:

> Does the mouse's current distributed wave/neural state *before* visual evidence arrives
> add information about whether that evidence will become behaviorally effective?

The answer so far is not a clean yes or no. Several attractive versions failed, while one
phase result remains genuinely interesting but methodologically entangled.

---

## 1. Public-code audit: three load-bearing problems

### 1.1 SEM denominator mismatch

`task/plots/plotHitRate2_8Hz.m` explicitly uses four mice:

```matlab
fname = {'ZYE_0085','ZYE_0088','ZYE_0090','ZYE_0091'};
hit_rate_high = nan(5,4);
...
```

but later computes:

```matlab
hit_rate_change_sem = std(hit_rate_change,2)./sqrt(6)
```

(the actual MATLAB call includes the dimension arguments around `std`; the important
point is the `sqrt(6)`). The analogous slow-band plotting code also uses `sqrt(6)`.
For four mice, this makes the plotted SEM about 18.4% smaller than `SD/sqrt(4)`.
The inferential ANOVA block in the 2-8 Hz plot is commented out, so this is primarily a
plot/error-bar bug, not by itself a refutation of the phase effect.

### 1.2 The plotted "onset phase" is not cleanly pre-stimulus

`getTrialTraceTask3.m` aligns each trial with:

```matlab
indx = find(t-allPD2(i)>0,1,'first');
```

Thus MATLAB trial sample 141 is the **first imaging frame after the photodiode time**.
`plotHitRate2_8Hz.m` reads:

```matlab
phase1 = squeeze(phase_all(141,1,:));
```

Moreover the stored phase and amplitude are produced on the continuous trace by:

```matlab
traceFilt = filtfilt(...)
traceHilbert = hilbert(traceFilt)
```

before trials are cut out. Both are offline/acausal operations. Therefore the public code,
as written, cannot establish that the value called "phase" at sample 141 is a causal
measurement of neural state before evidence arrives.

This does **not** imply that the effect is necessarily an artifact. Later controls below
show that the onset phase is substantially forecastable from genuinely earlier raw data.

### 1.3 Correct/incorrect/miss spiral-density maps are not stimulus-side matched

`getCorrectSpiralDensity.m` constructs the groups differently:

```matlab
correct:
    label == "correct" AND (left_contrast - right_contrast) > 0

incorrect / miss:
    matching label AND abs(left_contrast - right_contrast) > 0
```

The correct map therefore contains one stimulus side, whereas incorrect and miss contain
both. `plotCorrectSpiralDensity.m` then displays these as Correct / Incorrect / Miss.
Any lateral/topographic difference can consequently mix success state with stimulus-side
geometry.

The earlier `getTaskSpirals.m` retains left/right groups separately, so the raw per-trial
spiral product is reparable; the confound enters the later density summary.

---

## 2. Independent gate A: raw past-only neural state

A deliberately plain behavioral readout used only raw `wf_all`, with no filtered phase,
Hilbert transform, or post-stimulus samples.

Frozen features:

```text
baseline:
    stimulus contrast + side

local:
    baseline + raw V1 history from about -1.0 to -0.2 s

multi:
    baseline + the same raw history from all six sampled sites
```

Evaluation used contiguous held-out trial blocks. The first two mice were development;
the same specification was then run on the other two without tuning.

Held-out log loss (lower is better):

```text
ZYE_0088   baseline 0.55923   local 0.57237   multi 0.63478
ZYE_0090   baseline 0.45524   local 0.45690   multi 0.47903

ZYE_0085   baseline 0.41981   local 0.42357   multi 0.43772
ZYE_0091   baseline 0.41105   local 0.41265   multi 0.42120
```

A post-hoc optimistic regularization sweep still failed to make the neural models beat
the best baseline in any mouse.

Verdict:

> **This simple linear past-only raw-state readout fails.**

Do not generalize this to "pre-stimulus state is irrelevant." It only rejects this
particular low-dimensional linear readout.

---

## 3. Independent gate B: pre-stimulus spiral occurrence / mean geometry

The authors' per-trial spiral files contain a `trial x 141-frame` cell array aligned to
relative frames `-70..+70`. ZYE_0088 alone was used to freeze a compact readout before
opening the other three spiral files.

Frozen windows:

```text
safe  relative frames -35..-14  ~ -1000..-400 ms
near  relative frames -13..-3   ~ -371..-86 ms
```

Frozen summaries per window:

```text
spiral count
mean x
mean y
mean radius
mean direction
```

Frozen classifier:

```text
contrast + side baseline
5 contiguous folds
StandardScaler + LogisticRegression(C=0.1)
```

Development mouse ZYE_0088 already showed degradation:

```text
baseline                 log loss 0.559076
+ safe count                       0.560315
+ safe geometry                    0.562639
+ safe + near geometry             0.567917
```

The three unopened subject holdouts did not rescue it:

```text
ZYE_0085
baseline                 0.419304
+ safe count              0.419279   (tiny ~2.5e-5 improvement)
+ safe geometry           0.420663
+ safe + near geometry    0.419966

ZYE_0090
baseline                 0.452713
+ safe count              0.452618   (tiny ~9.5e-5 improvement)
+ safe geometry           0.453884
+ safe + near geometry    0.455654

ZYE_0091
baseline                 0.411013
+ safe count              0.411431
+ safe geometry           0.411767
+ safe + near geometry    0.411792
```

Across held-outs, `safe geometry` and `safe+near geometry` worsened mean log loss; neither
improved log loss in any of the three held-out mice. Count alone was effectively zero.

Verdict:

> **Simple pre-stimulus spiral occurrence and mean geometry do not add useful held-out
> behavioral information under this frozen readout.**

Again, this is not a generic wave null. Mean summaries can erase structured spatial phase,
and the spiral detector itself was generated by the authors' offline phase pipeline.

Workflow run: `31626870965`.

---

## 4. The authors' exact phase split really is positive

The public `plotHitRate2_8Hz.m` analysis was reproduced directly from the deposited
processed files.

Their exact eligibility rule is:

```text
2-8 Hz amplitude:
    mean samples 123:141, V1
    keep > 25th percentile

0.05-2 Hz amplitude:
    mean samples 1:141, V1
    keep < 25th percentile
```

Then phase at sample 141 is split into:

```text
A: -pi/2 < phase < +pi/2
B: complementary half-cycle
```

Equal-weighted hit-rate difference A-B across the five contrasts:

```text
ZYE_0085   +0.0293
ZYE_0088   +0.0647
ZYE_0090   +0.0589
ZYE_0091   +0.0193
mean       +0.0431
```

More importantly, the aggregate effect is concentrated at low visual contrast:

```text
6% contrast       +0.1351
12.5%             +0.1276
25%               -0.0017
50%               -0.0096
100%              -0.0361
```

So the exact public-code positive is not imaginary; near threshold, one phase half has a
substantially higher hit rate than the other in this selected subset.

The correct four-mouse SEM for the two low-contrast differences is approximately 0.0470
and 0.0624. The public `sqrt(6)` code yields smaller ~0.0384 and ~0.0510 values.

### A correction to our own first reaction

Moving the same fixed phase half backward by 200 ms made the sign reverse, but that is
**not** by itself evidence of leakage: a 2-8 Hz oscillatory phase naturally rotates, so a
fixed half-cycle label need not retain the same sign at an earlier time. Do not use that
lag-sign reversal as an argument against the phase effect.

Workflow run: `31626192470`.

---

## 5. External gate C: can the onset phase itself be forecast from pre-event raw V1?

This is the most interesting surviving boundary.

On development mouse ZYE_0088, several past windows were inspected. The strongest simple
forecast used only raw V1 samples at relative frames `-7..-1` (~-200 to -29 ms), excluding
the authors' sample 141. That window was then frozen before opening the other three mice.

Target:

```text
authors' onset phase half at sample 141
```

Predictor:

```text
raw V1 -7..-1
5 contiguous folds
StandardScaler + LogisticRegression(C=0.1)
```

Phase-half forecast AUC:

```text
ZYE_0088 development   0.8294

held-out:
ZYE_0085               0.8147
ZYE_0090               0.8049
ZYE_0091               0.8342
held-out mean          0.8179
```

This matters because it blocks the easy dismissal:

> The authors' onset phase is **substantially predictable from raw activity that occurred
> before the first post-photodiode imaging frame**.

Therefore the onset phase is at least partly a continuation/readout of prior state, even
though the public phase estimate itself is offline/acausal.

---

## 6. Does the forecastable pre-state carry the behavioral effect?

For this diagnostic only, the authors' exact amplitude eligibility was retained and the
analysis was restricted to 6% and 12.5% contrast, where their effect lives.

This is *not* a causal behavior analysis because eligibility itself uses acausally
filtered amplitude through sample 141. It asks only whether the public positive survives
when actual onset phase identity is replaced by a phase-group forecast generated from
pre-event raw V1.

Development:

```text
ZYE_0088   n=39
actual onset phase hit difference      +0.2395
forecast pre-stim phase hit difference +0.0353
```

Held-out subjects:

```text
            actual onset     forecast from raw pre-state
ZYE_0085     +0.0745             +0.0364
ZYE_0090     +0.2202             +0.1124
ZYE_0091     +0.0192             -0.0532

mean          +0.1046             +0.0319
positive       3 / 3               2 / 3
```

So two statements are simultaneously true:

1. **The onset phase itself is robustly forecastable from pre-event raw activity.**
2. **The behavior-linked phase difference is only partially and inconsistently recovered
   by this simple pre-event forecast.**

This is not a clean confirmation of a pre-stimulus accessibility state, and it is not a
clean artifact result either.

Workflow run: `31627405562`.

---

## 7. Important conditioning dependence

A simple exploratory check without the authors' amplitude eligibility found that the
low-contrast phase-behavior difference largely disappeared. Across all low-contrast
trials, the actual onset half-cycle difference was small/mixed except in one mouse, and
the pre-event forecast group was similarly near zero/mixed.

Therefore the striking phase/hit relationship is not simply:

```text
phase -> perception
```

It is closer to:

```text
particular amplitude/state regime
        x
phase
        -> different hit probability near threshold
```

The problem is that the current public definition of that amplitude/state regime is
itself constructed with offline/acausal values through onset.

That is now the load-bearing unresolved piece.

---

## 8. Current verdict

What the external data have rejected:

```text
simple raw -1.0..-0.2 s linear state readout              FAIL
simple six-site distributed raw readout                   FAIL
simple pre-stim spiral count                              ~NULL
simple pre-stim mean spiral geometry                      FAIL
"global wave geometry obviously predicts perception"      NOT SUPPORTED
```

What survives:

```text
authors' amplitude-conditioned near-threshold onset phase effect   REAL IN THEIR DATA
onset phase forecastable from raw pre-event V1                     ROBUST ACROSS 4 MICE
behavioral effect in forecasted phase                              WEAKER / MIXED
```

The strongest defensible sentence at this point is:

> **The mouse's raw pre-event V1 state contains substantial information about the phase
> state measured at stimulus onset, but we have not yet shown that the forecastable part
> of that state robustly explains the subsequent detection advantage.**

That is narrower than the PresentMoment framework hoped for, and therefore more useful.

---

## 9. The next gate, if reopened

Do not add another conceptual layer. The remaining empirical question is whether the
state-conditioning that exposes the phase/hit effect can itself be defined from
**past-only information**.

A legitimate next test would freeze, on one development mouse, a pre-event-only proxy for
the authors' high-2-8-Hz / low-slow-amplitude regime, then evaluate the resulting
phase-by-state interaction on unopened subjects/sessions.

If a genuinely pre-event-only state proxy reproduces the near-threshold phase effect,
then the accessibility interpretation gains real ground.

If it does not, stop using this task as evidence for a pre-stimulus accessibility surface.

No new name is needed either way.
