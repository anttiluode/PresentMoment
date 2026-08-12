#!/usr/bin/env python3
"""Reproduce and time-shift the Ye et al. task phase/hit-rate analysis.

This is an external audit of the public 2026 task data/code associated with
"Brain-wide topographic coordination of traveling spiral waves".

The authors' plotHitRate2_8Hz.m does the following for four mice:
  * 2-8 Hz amplitude: keep trials above the 25th percentile using samples 123:141
  * 0.05-2 Hz amplitude: keep trials below the 25th percentile using samples 1:141
  * read 2-8 Hz phase at sample 141, channel 1
  * split phase into (-pi/2,+pi/2) versus the complementary half-cycle
  * report hit/correct rate at five stimulus contrasts

Their getTrialTraceTask3.m makes MATLAB sample 141 the first widefield frame after the
photodiode onset (`find(t-allPD2(i)>0,1,'first')`).  The stored phase/amplitude were also
computed with filtfilt + Hilbert on the continuous trace, so this script does NOT call
any of these phase samples causal or genuinely pre-stimulus.

Two outputs are produced:
  1. exact code-level reproduction at the authors' sample 141;
  2. a fixed phase-sample lag sweep (0, -200, -400, -800, -1200 ms) while leaving the
     authors' amplitude-selection rule unchanged.

The lag sweep is only a leakage/timing sensitivity check.  The selection variables
remain acausally filtered and end at sample 141.
"""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

import h5py
import numpy as np
from remotezip import RemoteZip

ARTICLE = 27850542
MICE = ("ZYE_0085", "ZYE_0088", "ZYE_0090", "ZYE_0091")
CONTRASTS = np.array([0.06, 0.125, 0.25, 0.5, 1.0], dtype=float)
FS = 35.0
# Relative to MATLAB sample 141 / Python index 140. 0 is the authors' exact sample.
LAGS_MS = (0, -200, -400, -800, -1200)
OUT = Path("results/ye_task_phase_reproduction.json")


def get_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "PresentMoment-phase-audit/1.0"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def matlab_char(f: h5py.File, ref) -> str:
    a = np.asarray(f[ref]).ravel()
    return "".join(chr(int(x)) for x in a)


def load_matlab_table(path: Path) -> dict[str, np.ndarray]:
    """Decode the specific MATLAB-v7.3 table layout used by the deposited T_all files."""
    with h5py.File(path, "r") as f:
        mcos = f["#subsystem#/MCOS"][0]
        data_cell = f[mcos[2]]
        names_cell = f[mcos[7]]
        names = [matlab_char(f, r) for r in names_cell[:, 0]]
        cols: dict[str, np.ndarray] = {}
        for name, ref in zip(names, data_cell[:, 0]):
            obj = f[ref]
            cls = obj.attrs.get("MATLAB_class", b"")
            if isinstance(cls, bytes):
                cls = cls.decode()
            if cls == "cell":
                refs = obj[0, :] if obj.shape[0] == 1 else obj[:, 0]
                cols[name] = np.array([matlab_char(f, rr) for rr in refs], dtype=object)
            else:
                cols[name] = np.asarray(obj).squeeze()
        return cols


def extract_member(rz: RemoteZip, name: str, dest: Path) -> None:
    z = rz.getinfo(name)
    print(f"extract {name}: {z.file_size/1024/1024:.2f} MiB", flush=True)
    with rz.open(z) as src, dest.open("wb") as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            dst.write(chunk)


def safe_rate(x: np.ndarray) -> float | None:
    return float(np.mean(x)) if x.size else None


def one_mouse(mouse: str, high_path: Path, low_path: Path, outcome_path: Path) -> dict:
    tab = load_matlab_table(outcome_path)
    y = np.asarray(tab["correct"], float)
    abs_contrast = np.abs(np.asarray(tab["left_contrast"]) - np.asarray(tab["right_contrast"]))

    with h5py.File(high_path, "r") as f8, h5py.File(low_path, "r") as f2:
        n = f8["phase_all"].shape[0]
        if len(y) != n or f2["amp_all"].shape[0] != n:
            raise RuntimeError(f"trial mismatch for {mouse}: outcome={len(y)}, high={n}, low={f2['amp_all'].shape[0]}")

        # Exact MATLAB 1-based windows translated to Python slices.
        amp8 = np.asarray(f8["amp_all"][:, 0, 122:141]).mean(axis=1)   # 123:141
        amp2 = np.asarray(f2["amp_all"][:, 0, 0:141]).mean(axis=1)     # 1:141
        p8 = float(np.percentile(amp8, 25))
        p2 = float(np.percentile(amp2, 25))
        eligible = (amp8 > p8) & (amp2 < p2)

        lag_rows = {}
        for lag_ms in LAGS_MS:
            idx = 140 + int(round(lag_ms * FS / 1000.0))
            phase = np.asarray(f8["phase_all"][:, 0, idx])
            half_a = eligible & (phase > -np.pi / 2) & (phase < np.pi / 2)
            half_b = eligible & ((phase < -np.pi / 2) | (phase > np.pi / 2))

            a_rates = []
            b_rates = []
            counts = []
            diffs = []
            for c in CONTRASTS:
                a = half_a & (abs_contrast == c)
                b = half_b & (abs_contrast == c)
                ra = safe_rate(y[a])
                rb = safe_rate(y[b])
                a_rates.append(ra)
                b_rates.append(rb)
                counts.append({"contrast": float(c), "half_a_n": int(a.sum()), "half_b_n": int(b.sum())})
                diffs.append(None if ra is None or rb is None else float(ra - rb))

            finite = [d for d in diffs if d is not None and math.isfinite(d)]
            lag_rows[str(lag_ms)] = {
                "python_time_index": int(idx),
                "matlab_time_index": int(idx + 1),
                "half_a_total_n": int(half_a.sum()),
                "half_b_total_n": int(half_b.sum()),
                "hit_rate_half_a": a_rates,
                "hit_rate_half_b": b_rates,
                "half_a_minus_b": diffs,
                "equal_contrast_mean_difference": float(np.mean(finite)) if finite else None,
                "counts": counts,
            }

    return {
        "mouse": mouse,
        "n_trials": int(len(y)),
        "eligible_n": int(eligible.sum()),
        "amp8_p25": p8,
        "amp2_p25": p2,
        "lags": lag_rows,
    }


def aggregate(subjects: list[dict]) -> dict:
    out = {}
    for lag_ms in LAGS_MS:
        key = str(lag_ms)
        mat = np.array(
            [[np.nan if x is None else x for x in s["lags"][key]["half_a_minus_b"]] for s in subjects],
            dtype=float,
        )
        subj_mean = np.nanmean(mat, axis=1)
        contrast_mean = np.nanmean(mat, axis=0)
        # MATLAB std defaults to N-1.  The public plot divides by sqrt(6), despite 4 mice.
        contrast_sd = np.nanstd(mat, axis=0, ddof=1)
        out[key] = {
            "subject_equal_contrast_mean_differences": subj_mean.tolist(),
            "mean_across_subjects": float(np.nanmean(subj_mean)),
            "contrast_mean_differences": contrast_mean.tolist(),
            "contrast_sem_correct_n4": (contrast_sd / math.sqrt(4)).tolist(),
            "contrast_sem_as_public_code_sqrt6": (contrast_sd / math.sqrt(6)).tolist(),
        }
    return out


def main() -> None:
    meta = get_json(f"https://api.figshare.com/v2/articles/{ARTICLE}")
    url = meta["files"][0]["download_url"]
    subjects = []
    with RemoteZip(url) as rz, tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for mouse in MICE:
            hp = td / f"{mouse}_8.mat"
            lp = td / f"{mouse}_2.mat"
            op = td / f"{mouse}_outcome.mat"
            extract_member(rz, f"task/task_outcome/{mouse}_task_freq_to8Hz.mat", hp)
            extract_member(rz, f"task/task_outcome/{mouse}_task_freq_to2Hz.mat", lp)
            extract_member(rz, f"task/task_outcome/{mouse}_task_outcome.mat", op)
            row = one_mouse(mouse, hp, lp, op)
            subjects.append(row)
            print(mouse, "eligible", row["eligible_n"], "t0 mean diff", row["lags"]["0"]["equal_contrast_mean_difference"], flush=True)
            hp.unlink(); lp.unlink(); op.unlink()

    result = {
        "source_article": ARTICLE,
        "mice": list(MICE),
        "fs_hz": FS,
        "authors_exact_sample_matlab_index": 141,
        "authors_exact_sample_note": "sample 141 is the first widefield frame after photodiode onset in getTrialTraceTask3.m",
        "lags_ms_relative_to_authors_sample": list(LAGS_MS),
        "guardrails": [
            "The stored phase/amplitude were computed with filtfilt and Hilbert on continuous traces; no lag here is treated as a causal phase estimate.",
            "The lag sweep changes only the phase sample. The authors' amplitude eligibility rule remains fixed and includes samples through index 141.",
            "The public plot uses four mice but computes SEM with sqrt(6); both the code value and the n=4 correction are reported.",
        ],
        "subjects": subjects,
        "aggregate": aggregate(subjects),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nAGGREGATE")
    for lag in LAGS_MS:
        r = result["aggregate"][str(lag)]
        print(lag, "subject means", [round(x, 4) for x in r["subject_equal_contrast_mean_differences"]], "mean", round(r["mean_across_subjects"], 5))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
