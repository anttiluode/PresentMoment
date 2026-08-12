#!/usr/bin/env python3
"""Frozen subject-holdout gate for pre-stimulus spiral summaries in Ye et al. task data.

Development subject: ZYE_0088 only.
Held-out subjects: ZYE_0085, ZYE_0090, ZYE_0091.

The feature specification is frozen from the ZYE_0088 exploration before opening the
held-out spiral files:

  baseline
      5 one-hot stimulus contrasts + stimulus side

  safe count
      baseline + number of spiral detections in relative frames -35..-14
      (~ -1.00 s to -0.40 s at 35 Hz)

  safe geometry
      baseline + [count, mean x, mean y, mean radius, mean direction]
      over the same safe window

  safe + near geometry
      baseline + the same 5 summaries in both:
          safe: -35..-14  (~ -1000..-400 ms)
          near: -13..-3   (~ -371..-86 ms)

For empty windows, count and geometry summaries are zero. Geometry is normalized by
atlas scale constants used by the public task code (x/1140, y/1320, radius/100).

Outcome:
    correct versus incorrect/miss, restricted to nonzero-contrast trials.

Evaluation:
    5 contiguous held-out trial blocks; StandardScaler + LogisticRegression
    C=0.1, solver=liblinear. No hyperparameter tuning is performed on held-outs.

This is deliberately a small, lossy readout. A null means only that these simple
pre-stimulus spiral occurrence/geometry summaries fail to add predictive information
under this frozen linear test. It does not mean brain state or traveling waves are
behaviorally irrelevant.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

import h5py
import numpy as np
from remotezip import RemoteZip
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler

ARTICLE = 27850542
MICE = ("ZYE_0088", "ZYE_0085", "ZYE_0090", "ZYE_0091")
DEV_MOUSE = "ZYE_0088"
HELDOUT = ("ZYE_0085", "ZYE_0090", "ZYE_0091")
CONTRASTS = np.array([0.06, 0.125, 0.25, 0.5, 1.0], dtype=float)
C = 0.1
SAFE = tuple(range(35, 57))   # HDF frame indexes = relative -35..-14
NEAR = tuple(range(57, 68))   # relative -13..-3
OUT = Path("results/ye_task_spiral_holdout_gate.json")


def get_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "PresentMoment-spiral-holdout/1.0"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def matlab_char(f: h5py.File, ref) -> str:
    a = np.asarray(f[ref]).ravel()
    return "".join(chr(int(x)) for x in a)


def load_matlab_table(f: h5py.File) -> dict[str, np.ndarray]:
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


def summarize_window(f: h5py.File, frames: tuple[int, ...]) -> np.ndarray:
    """Return trial x 5: count, mean x, mean y, mean radius, mean direction."""
    sa = f["spiral_all"]
    n_trials = sa.shape[1]
    out = np.zeros((n_trials, 5), dtype=np.float64)
    for trial in range(n_trials):
        chunks = []
        for frame in frames:
            arr = np.asarray(f[sa[frame, trial]])
            # Nonempty task spiral cells are stored as 5 x N numeric matrices.
            # MATLAB empty [0 x 5] cells appear in this HDF5 file as a short metadata-like
            # vector, so require a true 2-D 5-row payload before accepting it.
            if arr.ndim == 2 and arr.shape[0] >= 5 and arr.shape[1] > 0:
                chunks.append(arr[:5, :].T.astype(np.float64, copy=False))
        if not chunks:
            continue
        a = np.vstack(chunks)
        out[trial, 0] = a.shape[0]
        out[trial, 1] = float(np.mean(a[:, 0])) / 1140.0
        out[trial, 2] = float(np.mean(a[:, 1])) / 1320.0
        out[trial, 3] = float(np.mean(a[:, 2])) / 100.0
        out[trial, 4] = float(np.mean(a[:, 3]))
    return out


def baseline_design(tab: dict[str, np.ndarray]):
    left = np.asarray(tab["left_contrast"], dtype=float)
    right = np.asarray(tab["right_contrast"], dtype=float)
    labels = np.asarray(tab["label"], dtype=object)
    abs_contrast = np.abs(left - right)
    valid = np.isin(labels, ["correct", "incorrect", "miss"]) & (abs_contrast > 0)
    y = (labels == "correct").astype(int)
    side = np.sign(left - right)
    contrast_cols = np.column_stack(
        [np.isclose(abs_contrast, c).astype(float) for c in CONTRASTS]
    )
    x = np.column_stack([contrast_cols, side])
    return valid, y, x, abs_contrast, side


def contiguous_cv(x: np.ndarray, y: np.ndarray, valid: np.ndarray) -> dict:
    ids = np.flatnonzero(valid)
    xv = x[ids]
    yv = y[ids]
    n = len(ids)
    fold_id = np.floor(np.arange(n) * 5 / n).astype(int)
    pred = np.zeros(n, dtype=float)
    fold_rows = []
    for fold in range(5):
        tr = fold_id != fold
        te = fold_id == fold
        scaler = StandardScaler()
        xtr = scaler.fit_transform(xv[tr])
        xte = scaler.transform(xv[te])
        model = LogisticRegression(C=C, solver="liblinear", max_iter=1000)
        model.fit(xtr, yv[tr])
        p = model.predict_proba(xte)[:, 1]
        pred[te] = p
        fold_rows.append(
            {
                "fold": fold,
                "n_train": int(tr.sum()),
                "n_test": int(te.sum()),
                "test_correct_rate": float(np.mean(yv[te])),
                "log_loss": float(log_loss(yv[te], p, labels=[0, 1])),
                "auc": float(roc_auc_score(yv[te], p)) if len(np.unique(yv[te])) == 2 else None,
            }
        )
    return {
        "n": n,
        "correct_rate": float(np.mean(yv)),
        "log_loss": float(log_loss(yv, pred, labels=[0, 1])),
        "auc": float(roc_auc_score(yv, pred)),
        "folds": fold_rows,
    }


def one_mouse(path: Path, mouse: str) -> dict:
    with h5py.File(path, "r") as f:
        tab = load_matlab_table(f)
        safe = summarize_window(f, SAFE)
        near = summarize_window(f, NEAR)

    valid, y, base, abs_contrast, side = baseline_design(tab)
    designs = {
        "baseline": base,
        "safe_count": np.column_stack([base, safe[:, 0]]),
        "safe_geometry": np.column_stack([base, safe]),
        "safe_plus_near_geometry": np.column_stack([base, safe, near]),
    }
    scores = {name: contiguous_cv(x, y, valid) for name, x in designs.items()}
    b = scores["baseline"]
    for name, row in scores.items():
        row["delta_log_loss_vs_baseline"] = float(row["log_loss"] - b["log_loss"])
        row["delta_auc_vs_baseline"] = float(row["auc"] - b["auc"])

    return {
        "mouse": mouse,
        "role": "development" if mouse == DEV_MOUSE else "heldout_subject",
        "n_all_trials": int(len(y)),
        "n_valid_trials": int(valid.sum()),
        "safe_mean_spiral_count": float(np.mean(safe[valid, 0])),
        "safe_zero_fraction": float(np.mean(safe[valid, 0] == 0)),
        "near_mean_spiral_count": float(np.mean(near[valid, 0])),
        "near_zero_fraction": float(np.mean(near[valid, 0] == 0)),
        "scores": scores,
    }


def main() -> None:
    meta = get_json(f"https://api.figshare.com/v2/articles/{ARTICLE}")
    url = meta["files"][0]["download_url"]
    rows = []
    with RemoteZip(url) as rz, tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for mouse in MICE:
            member = f"task/spirals/{mouse}_spirals_task_sort.mat"
            dest = td / f"{mouse}.mat"
            extract_member(rz, member, dest)
            row = one_mouse(dest, mouse)
            rows.append(row)
            dest.unlink()
            print(f"\n{mouse} ({row['role']})", flush=True)
            for name, score in row["scores"].items():
                print(
                    f"  {name:24s} logloss={score['log_loss']:.6f} "
                    f"dLL={score['delta_log_loss_vs_baseline']:+.6f} "
                    f"auc={score['auc']:.6f} dAUC={score['delta_auc_vs_baseline']:+.6f}",
                    flush=True,
                )

    held = [r for r in rows if r["mouse"] in HELDOUT]
    model_names = tuple(rows[0]["scores"].keys())
    aggregate = {}
    for name in model_names:
        dll = np.array([r["scores"][name]["delta_log_loss_vs_baseline"] for r in held])
        dauc = np.array([r["scores"][name]["delta_auc_vs_baseline"] for r in held])
        aggregate[name] = {
            "heldout_mean_delta_log_loss_vs_baseline": float(np.mean(dll)),
            "heldout_subjects_better_log_loss": int(np.sum(dll < 0)),
            "heldout_mean_delta_auc_vs_baseline": float(np.mean(dauc)),
            "heldout_subjects_better_auc": int(np.sum(dauc > 0)),
        }

    result = {
        "source_article": ARTICLE,
        "development_mouse": DEV_MOUSE,
        "heldout_subjects": list(HELDOUT),
        "frozen_specification": {
            "safe_relative_frames": [-35, -14],
            "safe_approx_ms": [-1000, -400],
            "near_relative_frames": [-13, -3],
            "near_approx_ms": [-371, -86],
            "baseline": "five contrast one-hot columns + stimulus side",
            "spiral_geometry": "count, mean x/1140, mean y/1320, mean radius/100, mean direction; zeros if empty",
            "classifier": "StandardScaler + LogisticRegression(C=0.1, solver=liblinear)",
            "cv": "5 contiguous trial blocks",
        },
        "guardrails": [
            "ZYE_0088 alone was used to choose/freeze the two windows, summaries, classifier C, and candidate models before inspecting held-out spiral files.",
            "A null applies only to these simple occurrence/mean-geometry summaries and this linear readout.",
            "The spiral detections themselves originate from the authors' offline phase-based pipeline; moving the window farther before onset reduces but does not magically make that detector causal.",
            "No hyperparameter tuning or feature changes are performed after held-out subject results are seen.",
        ],
        "subjects": rows,
        "heldout_aggregate": aggregate,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nHELDOUT AGGREGATE", flush=True)
    for name, a in aggregate.items():
        print(name, json.dumps(a), flush=True)
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
