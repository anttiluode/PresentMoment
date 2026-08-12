#!/usr/bin/env python3
"""Audit the load-bearing RepOD cross-band eigenmode coupling metric.

This deliberately reproduces the Geometric-Neuron metric first, then attacks only
properties that a physical/geometric coupling measure ought to be invariant to:

1) arbitrary renaming of eigenmode labels,
2) treating categorical mode identities with a label-invariant statistic (AMI),
3) using mode energy rather than squared temporal mean,
4) using 10-20 electrode geometry rather than a ring built from file order,
5) independent channel phase randomisation preserving each channel's power spectrum.

The goal is not to fit a better schizophrenia classifier. It is to learn what the
reported HC-vs-SZ effect is actually measuring.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
from pathlib import Path
import urllib.parse
import urllib.request
import warnings

import numpy as np
from scipy import signal
from scipy.stats import ttest_ind
from sklearn.metrics import adjusted_mutual_info_score

warnings.filterwarnings("ignore")

DATASET_PID = "doi:10.18150/repod.0107441"
API_ROOT = "https://repod.icm.edu.pl/api"
BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}
N_MODES = 6
WORD_DURATION_S = 0.5
MAX_COUPLING_THRESHOLD = 0.95
# Original paper excluded h14 and s07 after QC. We report both all-subject and
# exact-paper exclusion sets, but never tune exclusions based on this audit.
PAPER_EXCLUDE = {"h14.edf", "s07.edf"}


def http_json(url: str):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def ensure_dataset(outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    meta_url = (
        f"{API_ROOT}/datasets/:persistentId/?persistentId="
        + urllib.parse.quote(DATASET_PID, safe="")
    )
    meta = http_json(meta_url)
    files = meta["data"]["latestVersion"]["files"]
    wanted = []
    for item in files:
        df = item["dataFile"]
        label = df.get("filename", "")
        if not label.lower().endswith(".edf"):
            continue
        fid = int(df["id"])
        dest = outdir / label.lower()
        wanted.append(dest)
        if dest.exists() and dest.stat().st_size > 1_000_000:
            continue
        print(f"download {label} fileId={fid}", flush=True)
        url = f"{API_ROOT}/access/datafile/{fid}"
        urllib.request.urlretrieve(url, dest)
    return sorted(wanted)


def load_preprocess(path: Path, use_ica: bool = True):
    import mne

    raw = mne.io.read_raw_edf(path, preload=True, verbose=False)
    raw.filter(1.0, 45.0, verbose=False)
    if abs(float(raw.info["sfreq"]) - 250.0) > 1e-6:
        raw.resample(250.0, verbose=False)

    removed = 0
    if use_ica:
        try:
            ica = mne.preprocessing.ICA(
                n_components=min(15, len(raw.ch_names) - 1),
                random_state=42,
                max_iter=500,
                verbose=False,
            )
            ica.fit(raw, verbose=False)
            eog_indices = []
            ch_upper = [c.upper().replace(" ", "") for c in raw.ch_names]
            for fp in ("FP1", "FP2"):
                matches = [raw.ch_names[i] for i, c in enumerate(ch_upper) if fp in c]
                if matches:
                    try:
                        idx, _ = ica.find_bads_eog(raw, ch_name=matches[0], verbose=False)
                        eog_indices.extend(idx)
                    except Exception:
                        pass
            if not eog_indices:
                from scipy.stats import kurtosis
                src = ica.get_sources(raw).get_data()
                bad = np.where(kurtosis(src, axis=1) > 5.0)[0].tolist()
                eog_indices = bad[:3]
            eog_indices = sorted(set(eog_indices))
            if eog_indices:
                ica.exclude = eog_indices
                ica.apply(raw, verbose=False)
                removed = len(eog_indices)
        except Exception as exc:
            print(f"ICA failed {path.name}: {exc}", flush=True)

    data = raw.get_data()
    names = [c.upper().replace(" ", "") for c in raw.ch_names]
    return data, names, float(raw.info["sfreq"]), removed


def ring_modes(n_channels: int, n_modes: int = N_MODES) -> np.ndarray:
    A = np.zeros((n_channels, n_channels), float)
    for i in range(n_channels):
        A[i, (i + 1) % n_channels] = 1.0
        A[i, (i - 1) % n_channels] = 1.0
    L = np.diag(A.sum(axis=1)) - A
    _, V = np.linalg.eigh(L)
    return V[:, :n_modes]


def geometry_modes(ch_names: list[str], n_modes: int = N_MODES) -> np.ndarray:
    """4-NN graph from standard 10-20 electrode coordinates."""
    import mne

    montage = mne.channels.make_standard_montage("standard_1020")
    posdict = montage.get_positions()["ch_pos"]
    # Canonical case-insensitive lookup.
    lookup = {k.upper(): np.asarray(v, float) for k, v in posdict.items()}
    pts = []
    for ch in ch_names:
        key = ch.upper().replace(" ", "")
        if key not in lookup:
            raise KeyError(f"No standard_1020 coordinate for {ch}")
        pts.append(lookup[key])
    X = np.vstack(pts)
    d = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2)
    n = len(ch_names)
    A = np.zeros((n, n), float)
    # Symmetric 4-nearest-neighbour graph with inverse-distance weights.
    for i in range(n):
        nn = np.argsort(d[i])[1:5]
        for j in nn:
            w = 1.0 / max(d[i, j], 1e-9)
            A[i, j] = max(A[i, j], w)
            A[j, i] = max(A[j, i], w)
    L = np.diag(A.sum(axis=1)) - A
    _, V = np.linalg.eigh(L)
    return V[:, :n_modes]


def bandpass(seg: np.ndarray, sfreq: float, low: float, high: float) -> np.ndarray:
    b, a = signal.butter(4, [low / (sfreq / 2), high / (sfreq / 2)], btype="band")
    return signal.filtfilt(b, a, seg, axis=1)


def dominant_sequences(
    data: np.ndarray,
    sfreq: float,
    modes: np.ndarray,
    projection: str = "original",
    duration_s: float = 60.0,
) -> dict[str, np.ndarray]:
    n_channels = min(modes.shape[0], data.shape[0])
    n_samples = min(int(duration_s * sfreq), data.shape[1])
    x = data[:n_channels, :n_samples]
    word_len = int(WORD_DURATION_S * sfreq)
    n_words = n_samples // word_len
    out = {b: [] for b in BANDS}
    V = modes[:n_channels]

    for t in range(n_words):
        seg = x[:, t * word_len : (t + 1) * word_len]
        for bname, (lo, hi) in BANDS.items():
            y = bandpass(seg, sfreq, lo, hi)
            projected = y.T @ V  # time x modes
            if projection == "original":
                score = np.mean(projected, axis=0) ** 2
            elif projection == "energy":
                score = np.mean(projected ** 2, axis=0)
            else:
                raise ValueError(projection)
            out[bname].append(int(np.argmax(score)))
    return {k: np.asarray(v, int) for k, v in out.items()}


def integer_label_coupling(seq: dict[str, np.ndarray], perm=None) -> float:
    vals = []
    names = list(BANDS)
    if perm is None:
        perm = np.arange(N_MODES)
    perm = np.asarray(perm, int)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = perm[seq[names[i]]].astype(float)
            b = perm[seq[names[j]]].astype(float)
            if a.std() > 0 and b.std() > 0:
                vals.append(float(np.corrcoef(a, b)[0, 1]))
            else:
                vals.append(0.0)
    return float(np.mean(vals))


def ami_coupling(seq: dict[str, np.ndarray]) -> float:
    vals = []
    names = list(BANDS)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            vals.append(adjusted_mutual_info_score(seq[names[i]], seq[names[j]]))
    return float(np.mean(vals))


def same_mode_excess(seq: dict[str, np.ndarray]) -> float:
    """Observed same-label probability minus shuffled expectation, averaged over bands."""
    vals = []
    names = list(BANDS)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = seq[names[i]], seq[names[j]]
            obs = float(np.mean(a == b))
            pa = np.bincount(a, minlength=N_MODES) / len(a)
            pb = np.bincount(b, minlength=N_MODES) / len(b)
            exp = float(np.dot(pa, pb))
            vals.append(obs - exp)
    return float(np.mean(vals))


def phase_randomize_channels(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Independent phase randomisation per channel; exact Fourier magnitudes preserved."""
    out = np.empty_like(x)
    n = x.shape[1]
    for c in range(x.shape[0]):
        z = np.fft.rfft(x[c])
        mag = np.abs(z)
        phase = np.angle(z)
        if len(z) > 2:
            phase[1:-1] = rng.uniform(0, 2 * np.pi, len(z) - 2)
        zz = mag * np.exp(1j * phase)
        zz[0] = z[0]
        if n % 2 == 0:
            zz[-1] = z[-1]
        out[c] = np.fft.irfft(zz, n=n)
    return out


def effect(hc: list[float], sz: list[float]) -> dict:
    hc = np.asarray(hc, float)
    sz = np.asarray(sz, float)
    t, p = ttest_ind(hc, sz, equal_var=True)
    pooled = math.sqrt(((len(hc)-1)*hc.var(ddof=1) + (len(sz)-1)*sz.var(ddof=1)) / (len(hc)+len(sz)-2))
    d = (sz.mean() - hc.mean()) / pooled if pooled > 0 else float("nan")
    return {
        "hc_mean": float(hc.mean()),
        "sz_mean": float(sz.mean()),
        "t_hc_minus_sz": float(t),
        "p": float(p),
        "cohen_d_sz_minus_hc": float(d),
        "n_hc": int(len(hc)),
        "n_sz": int(len(sz)),
    }


def group_split(rows, key, paper_exclusion=True):
    use = [r for r in rows if (not paper_exclusion or r["file"] not in PAPER_EXCLUDE)]
    hc = [r[key] for r in use if r["group"] == "HC"]
    sz = [r[key] for r in use if r["group"] == "SZ"]
    return effect(hc, sz)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/repod_schizophrenia")
    ap.add_argument("--out", default="results/repod-geometric-metric-audit.json")
    ap.add_argument("--surrogates", type=int, default=8)
    ap.add_argument("--no-ica", action="store_true")
    args = ap.parse_args()

    paths = ensure_dataset(Path(args.data))
    print(f"EDF files={len(paths)}", flush=True)
    rows = []
    rng = np.random.default_rng(20260812)

    for k, path in enumerate(paths, 1):
        group = "HC" if path.name.startswith("h") else "SZ"
        print(f"[{k:02d}/{len(paths)}] {path.name} {group}", flush=True)
        data, ch_names, sfreq, removed = load_preprocess(path, use_ica=not args.no_ica)
        n = min(19, data.shape[0])
        data = data[:n]
        ch_names = ch_names[:n]
        ring = ring_modes(n)
        geom = geometry_modes(ch_names)

        seq_orig = dominant_sequences(data, sfreq, ring, "original")
        seq_energy_ring = dominant_sequences(data, sfreq, ring, "energy")
        seq_energy_geom = dominant_sequences(data, sfreq, geom, "energy")

        row = {
            "file": path.name,
            "group": group,
            "ica_removed": removed,
            "original": integer_label_coupling(seq_orig),
            "original_ami": ami_coupling(seq_orig),
            "original_same_mode_excess": same_mode_excess(seq_orig),
            "energy_ring_integer": integer_label_coupling(seq_energy_ring),
            "energy_ring_ami": ami_coupling(seq_energy_ring),
            "energy_geom_integer": integer_label_coupling(seq_energy_geom),
            "energy_geom_ami": ami_coupling(seq_energy_geom),
            # Save sequences so the exact global mode-relabel audit can be done after all subjects.
            "orig_seq": {b: seq_orig[b].tolist() for b in BANDS},
            "phase_random_original": [],
        }

        # Spectrum-preserving null on the original metric.
        dur = min(int(60 * sfreq), data.shape[1])
        base = data[:, :dur]
        for s in range(args.surrogates):
            xr = phase_randomize_channels(base, rng)
            seq_r = dominant_sequences(xr, sfreq, ring, "original")
            row["phase_random_original"].append(integer_label_coupling(seq_r))
        rows.append(row)

    # Group summaries, exact paper exclusions and all 28 for transparency.
    keys = [
        "original", "original_ami", "original_same_mode_excess",
        "energy_ring_integer", "energy_ring_ami",
        "energy_geom_integer", "energy_geom_ami",
    ]
    summaries = {k: group_split(rows, k, True) for k in keys}
    summaries_all28 = {k: group_split(rows, k, False) for k in keys}

    # Mode-label invariance: exhaust all 6! global relabellings. Exact same categorical
    # trajectories, only names 0..5 are reassigned.
    perm_results = []
    clean = [r for r in rows if r["file"] not in PAPER_EXCLUDE]
    for perm in itertools.permutations(range(N_MODES)):
        hc, sz = [], []
        for r in clean:
            seq = {b: np.asarray(r["orig_seq"][b], int) for b in BANDS}
            v = integer_label_coupling(seq, perm=perm)
            (hc if r["group"] == "HC" else sz).append(v)
        e = effect(hc, sz)
        perm_results.append((perm, e))
    ps = np.asarray([e["p"] for _, e in perm_results])
    ds = np.asarray([e["cohen_d_sz_minus_hc"] for _, e in perm_results])
    original_perm = next(e for p, e in perm_results if tuple(p) == tuple(range(N_MODES)))
    best = min(perm_results, key=lambda z: z[1]["p"])
    worst = max(perm_results, key=lambda z: z[1]["p"])
    relabel = {
        "n_permutations": len(perm_results),
        "identity": original_perm,
        "p_min": float(ps.min()),
        "p_median": float(np.median(ps)),
        "p_max": float(ps.max()),
        "fraction_p_lt_0_05": float(np.mean(ps < 0.05)),
        "d_min": float(ds.min()),
        "d_max": float(ds.max()),
        "fraction_effect_sign_flip_vs_identity": float(np.mean(np.sign(ds) != np.sign(original_perm["cohen_d_sz_minus_hc"]))),
        "best_perm": {"perm": list(best[0]), **best[1]},
        "worst_perm": {"perm": list(worst[0]), **worst[1]},
    }

    # Phase-randomised group null: compare HC/SZ at each surrogate index.
    null_effects = []
    for s in range(args.surrogates):
        hc = [r["phase_random_original"][s] for r in clean if r["group"] == "HC"]
        sz = [r["phase_random_original"][s] for r in clean if r["group"] == "SZ"]
        null_effects.append(effect(hc, sz))
    null_ps = np.asarray([e["p"] for e in null_effects])
    null_ds = np.asarray([e["cohen_d_sz_minus_hc"] for e in null_effects])
    phase_null = {
        "replicates": args.surrogates,
        "p_values": null_ps.tolist(),
        "effect_ds": null_ds.tolist(),
        "p_median": float(np.median(null_ps)),
        "fraction_p_lt_0_05": float(np.mean(null_ps < 0.05)),
        "d_mean": float(np.mean(null_ds)),
    }

    # Strip bulky sequences from user-facing JSON rows after relabel audit.
    compact_rows = []
    for r in rows:
        rr = dict(r)
        rr.pop("orig_seq", None)
        compact_rows.append(rr)

    result = {
        "dataset": DATASET_PID,
        "paper_exclusions": sorted(PAPER_EXCLUDE),
        "surrogate_count": args.surrogates,
        "summaries_paper_n26": summaries,
        "summaries_all28": summaries_all28,
        "mode_relabel_invariance": relabel,
        "phase_randomized_original_metric": phase_null,
        "subjects": compact_rows,
        "guardrails": [
            "Relabel permutations preserve every dominant-mode trajectory; only arbitrary integer names change.",
            "AMI is invariant to categorical label permutations.",
            "Independent phase randomisation preserves each channel's Fourier magnitudes but destroys its timing relative to other channels.",
            "This audit does not claim any alternative metric is clinically valid; it asks whether the original interpretation survives basic invariances/nulls.",
        ],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))

    print("\n=== PAPER-EXCLUSION n=26 ===")
    for k, e in summaries.items():
        print(f"{k:26s} HC={e['hc_mean']:+.4f} SZ={e['sz_mean']:+.4f} p={e['p']:.5g} d(SZ-HC)={e['cohen_d_sz_minus_hc']:+.3f}")
    print("\n=== MODE LABEL RELABEL AUDIT (6! exact) ===")
    print(json.dumps(relabel, indent=2))
    print("\n=== SPECTRUM-PRESERVING PHASE NULL ===")
    print(json.dumps(phase_null, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
