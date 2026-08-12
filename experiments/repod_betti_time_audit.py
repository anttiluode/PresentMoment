#!/usr/bin/env python3
"""Audit the temporal-lobe persistent-homology result in Geometric-Neuron.

The published text describes a "Betti-1" loop count at Takens delays 10,20,40 ms.
The implementation instead:
  * passes delays 10,20,40 as *samples* at 250 Hz = 40,80,160 ms;
  * reports the sum of thresholded H1 lifetimes (total persistence), not a loop count.

This script reproduces that implementation, then separates those choices and asks
whether the HC-vs-SZ effect survives Fourier phase randomisation that preserves each
subject's temporal-region power spectrum exactly.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request
import warnings

import numpy as np
from scipy.stats import ttest_ind

warnings.filterwarnings("ignore")

DATASET_PID = "doi:10.18150/repod.0107441"
API_ROOT = "https://repod.icm.edu.pl/api"
PAPER_EXCLUDE = {"h14.edf", "s07.edf"}
TEMPORAL = ("T3", "T4", "T5", "T6", "T7", "T8", "TP7", "TP8")


def http_json(url: str):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def ensure_dataset(outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    meta_url = f"{API_ROOT}/datasets/:persistentId/?persistentId=" + urllib.parse.quote(DATASET_PID, safe="")
    meta = http_json(meta_url)
    files = meta["data"]["latestVersion"]["files"]
    paths = []
    for item in files:
        df = item["dataFile"]
        name = df.get("filename", "").lower()
        if not name.endswith(".edf"):
            continue
        dest = outdir / name
        paths.append(dest)
        if not (dest.exists() and dest.stat().st_size > 1_000_000):
            fid = int(df["id"])
            print(f"download {name} fileId={fid}", flush=True)
            urllib.request.urlretrieve(f"{API_ROOT}/access/datafile/{fid}", dest)
    return sorted(paths)


def load_temporal(path: Path, use_ica=True):
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
                random_state=42, max_iter=500, verbose=False
            )
            ica.fit(raw, verbose=False)
            eog_indices = []
            names = [c.upper().replace(" ", "") for c in raw.ch_names]
            for fp in ("FP1", "FP2"):
                matches = [raw.ch_names[i] for i,c in enumerate(names) if fp in c]
                if matches:
                    try:
                        idx, _ = ica.find_bads_eog(raw, ch_name=matches[0], verbose=False)
                        eog_indices.extend(idx)
                    except Exception:
                        pass
            if not eog_indices:
                from scipy.stats import kurtosis
                src = ica.get_sources(raw).get_data()
                eog_indices = np.where(kurtosis(src, axis=1) > 5.0)[0].tolist()[:3]
            eog_indices = sorted(set(eog_indices))
            if eog_indices:
                ica.exclude = eog_indices
                ica.apply(raw, verbose=False)
                removed = len(eog_indices)
        except Exception as exc:
            print(f"ICA failed {path.name}: {exc}", flush=True)

    data = raw.get_data()
    names = [c.upper().replace(" ", "") for c in raw.ch_names]
    idx = [i for i,c in enumerate(names) if any(tag in c for tag in TEMPORAL)]
    if not idx:
        raise RuntimeError(f"no temporal channels in {path.name}: {names}")
    n = min(int(60 * raw.info["sfreq"]), data.shape[1])
    sig = data[idx, :n].mean(axis=0)
    return sig, float(raw.info["sfreq"]), removed, [names[i] for i in idx]


def takens3(x: np.ndarray, delay_samples: int):
    d = int(delay_samples)
    n = len(x) - 2*d
    if n < 10:
        raise ValueError("too short")
    X = np.column_stack([x[2*d:], x[d:d+n], x[:n]])
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-10)
    if len(X) > 500:
        ix = np.linspace(0, len(X)-1, 500, dtype=int)
        X = X[ix]
    return X


def h1_metrics(x: np.ndarray, delays: tuple[int,...], threshold_fraction=0.1):
    from ripser import ripser
    per_delay = []
    for d in delays:
        X = takens3(x, d)
        dgm = ripser(X, maxdim=1)["dgms"][1]
        if len(dgm) == 0:
            per_delay.append({"delay_samples": d, "total_persistence": 0.0, "count": 0, "max_lifetime": 0.0})
            continue
        life = dgm[:,1] - dgm[:,0]
        life = life[np.isfinite(life)]
        if not len(life):
            per_delay.append({"delay_samples": d, "total_persistence": 0.0, "count": 0, "max_lifetime": 0.0})
            continue
        mx = float(life.max())
        keep = life > threshold_fraction * mx
        per_delay.append({
            "delay_samples": d,
            "total_persistence": float(life[keep].sum()),
            "count": int(keep.sum()),
            "max_lifetime": mx,
        })
    return {
        "total_persistence": float(np.mean([z["total_persistence"] for z in per_delay])),
        "count": float(np.mean([z["count"] for z in per_delay])),
        "max_lifetime": float(np.mean([z["max_lifetime"] for z in per_delay])),
        "per_delay": per_delay,
    }


def phase_randomize(x: np.ndarray, rng: np.random.Generator):
    z = np.fft.rfft(x)
    mag = np.abs(z)
    ph = np.angle(z)
    if len(z) > 2:
        ph[1:-1] = rng.uniform(0, 2*np.pi, len(z)-2)
    zz = mag * np.exp(1j*ph)
    zz[0] = z[0]
    if len(x) % 2 == 0:
        zz[-1] = z[-1]
    return np.fft.irfft(zz, n=len(x))


def effect(rows, key):
    clean = [r for r in rows if r["file"] not in PAPER_EXCLUDE]
    hc = np.asarray([r[key] for r in clean if r["group"] == "HC"], float)
    sz = np.asarray([r[key] for r in clean if r["group"] == "SZ"], float)
    t,p = ttest_ind(hc, sz, equal_var=True)
    pooled = math.sqrt(((len(hc)-1)*hc.var(ddof=1)+(len(sz)-1)*sz.var(ddof=1))/(len(hc)+len(sz)-2))
    d = (sz.mean()-hc.mean())/pooled if pooled else float("nan")
    return {"hc_mean":float(hc.mean()),"sz_mean":float(sz.mean()),"p":float(p),"t_hc_minus_sz":float(t),"cohen_d_sz_minus_hc":float(d),"n_hc":len(hc),"n_sz":len(sz)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/repod_schizophrenia")
    ap.add_argument("--out", default="results/repod-betti-time-audit.json")
    ap.add_argument("--surrogates", type=int, default=4)
    ap.add_argument("--no-ica", action="store_true")
    args = ap.parse_args()

    paths = ensure_dataset(Path(args.data))
    rng = np.random.default_rng(20260812)
    rows=[]
    for k,path in enumerate(paths,1):
        group = "HC" if path.name.startswith("h") else "SZ"
        print(f"[{k:02d}/{len(paths)}] {path.name} {group}", flush=True)
        x,sfreq,removed,chs = load_temporal(path, use_ica=not args.no_ica)
        # Actual code delays.
        code_delays=(10,20,40)
        # Text-stated delays 10,20,40 ms, converted to nearest samples at 250 Hz.
        true_ms=tuple(max(1, int(round(ms*sfreq/1000.0))) for ms in (10,20,40))
        a=h1_metrics(x,code_delays)
        b=h1_metrics(x,true_ms)
        sur=[]
        for _ in range(args.surrogates):
            xr=phase_randomize(x,rng)
            sur.append({"code":h1_metrics(xr,code_delays),"true_ms":h1_metrics(xr,true_ms)})
        row={
            "file":path.name,"group":group,"sfreq":sfreq,"ica_removed":removed,"temporal_channels":chs,
            "code_delay_samples":list(code_delays),"code_delay_ms":[1000*d/sfreq for d in code_delays],
            "text_delay_samples":list(true_ms),"text_delay_ms":[1000*d/sfreq for d in true_ms],
            "code_total_persistence":a["total_persistence"],"code_count":a["count"],"code_max_lifetime":a["max_lifetime"],
            "text_total_persistence":b["total_persistence"],"text_count":b["count"],"text_max_lifetime":b["max_lifetime"],
            "sur_code_total_mean":float(np.mean([s["code"]["total_persistence"] for s in sur])),
            "sur_code_count_mean":float(np.mean([s["code"]["count"] for s in sur])),
            "sur_text_total_mean":float(np.mean([s["true_ms"]["total_persistence"] for s in sur])),
            "sur_text_count_mean":float(np.mean([s["true_ms"]["count"] for s in sur])),
        }
        row["code_total_excess_vs_phase_null"] = row["code_total_persistence"]-row["sur_code_total_mean"]
        row["code_count_excess_vs_phase_null"] = row["code_count"]-row["sur_code_count_mean"]
        row["text_total_excess_vs_phase_null"] = row["text_total_persistence"]-row["sur_text_total_mean"]
        row["text_count_excess_vs_phase_null"] = row["text_count"]-row["sur_text_count_mean"]
        rows.append(row)

    keys=[
        "code_total_persistence","code_count","code_max_lifetime",
        "text_total_persistence","text_count","text_max_lifetime",
        "sur_code_total_mean","sur_code_count_mean","sur_text_total_mean","sur_text_count_mean",
        "code_total_excess_vs_phase_null","code_count_excess_vs_phase_null",
        "text_total_excess_vs_phase_null","text_count_excess_vs_phase_null",
    ]
    summaries={k:effect(rows,k) for k in keys}
    result={
        "dataset":DATASET_PID,"paper_exclusions":sorted(PAPER_EXCLUDE),"surrogates_per_subject":args.surrogates,
        "important_definition_note":"Original compute_betti1 returns mean thresholded H1 lifetime SUM, not Betti-1 count.",
        "important_time_note":"Original delays=(10,20,40) are samples; at 250 Hz they are 40,80,160 ms, not the 10,20,40 ms stated in PAPER.md.",
        "summaries_n26":summaries,"subjects":rows,
        "guardrail":"Phase-randomized surrogates preserve each temporal-region signal's Fourier magnitude spectrum. If the group effect also appears in surrogate topology and vanishes after subject-level subtraction, the original topology result is substantially explained by second-order spectral/autocorrelation structure rather than nonlinear temporal geometry."
    }
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2))
    print("\n=== n=26 PAPER EXCLUSIONS ===")
    for k,e in summaries.items():
        print(f"{k:34s} HC={e['hc_mean']:+.4f} SZ={e['sz_mean']:+.4f} p={e['p']:.5g} d={e['cohen_d_sz_minus_hc']:+.3f}")
    print(f"\nwrote {out}")

if __name__ == "__main__":
    main()
