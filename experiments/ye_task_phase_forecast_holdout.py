#!/usr/bin/env python3
"""Can the behavior-linked Ye task onset phase be forecast from pre-stimulus raw V1?

Development mouse: ZYE_0088.
Held-out mice: ZYE_0085, ZYE_0090, ZYE_0091.

Why this gate
-------------
The public plot uses 2-8 Hz phase at MATLAB sample 141, which is the first widefield
frame after photodiode onset. The stored phase was made with filtfilt + Hilbert, so the
exact phase value is not a causal pre-stimulus estimate.

However, a genuinely ongoing pre-existing oscillatory state should leave enough trace in
raw activity *before* the event to forecast which half-cycle the onset estimate will enter.
On ZYE_0088 only, several past windows were inspected; the strongest simple forecast used
the last 7 raw V1 samples before sample 141. That choice is therefore development-tuned
and is frozen here before evaluating the other three mice.

Frozen forecast
---------------
Target:
    authors' onset half-cycle at sample 141:
      A = -pi/2 < phase < +pi/2
      B = complement

Input:
    raw `wf_all`, channel 1, relative frames -7..-1
    (~ -200 ms to -29 ms at 35 Hz), excluding the authors' sample 141 itself.

Model:
    5 contiguous trial folds; StandardScaler + LogisticRegression(C=0.1, liblinear).
    It is trained to predict phase half, never behavioral outcome.

Behavioral diagnostic:
    Reuse the authors' exact amplitude eligibility rule and restrict to the two lowest
    contrasts (0.06 and 0.125), where the public phase/hit effect is concentrated.
    Report correct-rate difference for:
      1. actual authors onset phase half;
      2. forecast phase half from pre-stim raw V1 only.

Important guardrail:
    The eligibility rule itself uses acausally filtered amplitude through sample 141, so
    the behavioral subset is NOT a causal analysis. This is a decomposition of the
    authors' positive: does the behavior-linked phase sign survive when phase identity is
    replaced by a forecast made solely from pre-event raw activity?
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
DEV = "ZYE_0088"
HELDOUT = ("ZYE_0085", "ZYE_0090", "ZYE_0091")
C = 0.1
RAW_SLICE = slice(133, 140)  # Python indexes; MATLAB 134:140 = rel -7..-1 before sample 141
LOW_CONTRASTS = (0.06, 0.125)
OUT = Path("results/ye_task_phase_forecast_holdout.json")


def get_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "PresentMoment-phase-forecast/1.0"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def matlab_char(f: h5py.File, ref) -> str:
    a = np.asarray(f[ref]).ravel()
    return "".join(chr(int(x)) for x in a)


def load_matlab_table(path: Path) -> dict[str, np.ndarray]:
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


def extract(rz: RemoteZip, member: str, dest: Path) -> None:
    z = rz.getinfo(member)
    print(f"extract {member}: {z.file_size/1024/1024:.2f} MiB", flush=True)
    with rz.open(z) as src, dest.open("wb") as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            dst.write(chunk)


def phase_forecast(raw: np.ndarray, group: np.ndarray) -> np.ndarray:
    n = len(group)
    fold_id = np.floor(np.arange(n) * 5 / n).astype(int)
    p = np.zeros(n, dtype=float)
    for fold in range(5):
        tr = fold_id != fold
        te = fold_id == fold
        scaler = StandardScaler()
        xtr = scaler.fit_transform(raw[tr])
        xte = scaler.transform(raw[te])
        model = LogisticRegression(C=C, solver="liblinear", max_iter=1000)
        model.fit(xtr, group[tr])
        p[te] = model.predict_proba(xte)[:, 1]
    return p


def rate_diff(y: np.ndarray, mask: np.ndarray, group: np.ndarray) -> dict:
    a = mask & group
    b = mask & ~group
    ra = float(np.mean(y[a])) if a.any() else None
    rb = float(np.mean(y[b])) if b.any() else None
    return {
        "half_a_n": int(a.sum()),
        "half_b_n": int(b.sum()),
        "half_a_correct_rate": ra,
        "half_b_correct_rate": rb,
        "half_a_minus_b": None if ra is None or rb is None else float(ra - rb),
    }


def one_mouse(mouse: str, high: Path, low: Path, outcome: Path) -> dict:
    tab = load_matlab_table(outcome)
    with h5py.File(high, "r") as f8, h5py.File(low, "r") as f2:
        raw = np.asarray(f8["wf_all"][:, 0, RAW_SLICE], dtype=float)
        phase = np.asarray(f8["phase_all"][:, 0, 140], dtype=float)
        amp8 = np.asarray(f8["amp_all"][:, 0, 122:141], dtype=float).mean(axis=1)
        amp2 = np.asarray(f2["amp_all"][:, 0, 0:141], dtype=float).mean(axis=1)

    actual_group = (phase > -np.pi / 2) & (phase < np.pi / 2)
    p_forecast = phase_forecast(raw, actual_group.astype(int))
    forecast_group = p_forecast >= 0.5

    left = np.asarray(tab["left_contrast"], dtype=float)
    right = np.asarray(tab["right_contrast"], dtype=float)
    labels = np.asarray(tab["label"], dtype=object)
    abs_contrast = np.abs(left - right)
    y = (labels == "correct").astype(int)
    valid = np.isin(labels, ["correct", "incorrect", "miss"]) & (abs_contrast > 0)

    eligibility = (amp8 > np.percentile(amp8, 25)) & (amp2 < np.percentile(amp2, 25))
    low = np.isin(abs_contrast, LOW_CONTRASTS)
    behavior_mask = valid & eligibility & low

    forecast_auc_all = float(roc_auc_score(actual_group, p_forecast))
    forecast_ll_all = float(log_loss(actual_group.astype(int), p_forecast, labels=[0, 1]))
    if behavior_mask.sum() and len(np.unique(actual_group[behavior_mask])) == 2:
        forecast_auc_behavior_subset = float(
            roc_auc_score(actual_group[behavior_mask], p_forecast[behavior_mask])
        )
    else:
        forecast_auc_behavior_subset = None

    return {
        "mouse": mouse,
        "role": "development" if mouse == DEV else "heldout_subject",
        "n_trials": int(len(y)),
        "phase_half_a_fraction": float(np.mean(actual_group)),
        "phase_forecast_auc_all_trials": forecast_auc_all,
        "phase_forecast_log_loss_all_trials": forecast_ll_all,
        "behavior_subset_n": int(behavior_mask.sum()),
        "phase_forecast_auc_behavior_subset": forecast_auc_behavior_subset,
        "actual_onset_phase_behavior": rate_diff(y, behavior_mask, actual_group),
        "forecast_prestim_phase_behavior": rate_diff(y, behavior_mask, forecast_group),
    }


def main() -> None:
    meta = get_json(f"https://api.figshare.com/v2/articles/{ARTICLE}")
    url = meta["files"][0]["download_url"]
    rows = []
    with RemoteZip(url) as rz, tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for mouse in MICE:
            high = td / f"{mouse}_8.mat"
            low = td / f"{mouse}_2.mat"
            out = td / f"{mouse}_out.mat"
            extract(rz, f"task/task_outcome/{mouse}_task_freq_to8Hz.mat", high)
            extract(rz, f"task/task_outcome/{mouse}_task_freq_to2Hz.mat", low)
            extract(rz, f"task/task_outcome/{mouse}_task_outcome.mat", out)
            row = one_mouse(mouse, high, low, out)
            rows.append(row)
            high.unlink(); low.unlink(); out.unlink()
            print(f"\n{mouse} {row['role']}")
            print(f"  forecast onset phase from prestim raw: AUC={row['phase_forecast_auc_all_trials']:.4f}")
            print(f"  low-contrast eligible n={row['behavior_subset_n']}")
            print(f"  actual onset phase hit diff: {row['actual_onset_phase_behavior']['half_a_minus_b']}")
            print(f"  forecast prestim phase hit diff: {row['forecast_prestim_phase_behavior']['half_a_minus_b']}", flush=True)

    held = [r for r in rows if r["mouse"] in HELDOUT]
    actual = np.array([r["actual_onset_phase_behavior"]["half_a_minus_b"] for r in held], dtype=float)
    forecast = np.array([r["forecast_prestim_phase_behavior"]["half_a_minus_b"] for r in held], dtype=float)
    phase_auc = np.array([r["phase_forecast_auc_all_trials"] for r in held], dtype=float)
    result = {
        "source_article": ARTICLE,
        "development_mouse": DEV,
        "heldout_subjects": list(HELDOUT),
        "frozen_specification": {
            "forecast_input": "raw wf_all channel 1, relative frames -7..-1 (~-200..-29 ms), no onset sample",
            "forecast_target": "authors onset 2-8 Hz phase half at MATLAB sample 141",
            "forecast_model": "5 contiguous-fold StandardScaler + LogisticRegression(C=0.1, liblinear)",
            "behavior_subset": "authors exact amplitude eligibility + contrasts 0.06 or 0.125",
        },
        "guardrails": [
            "The -7..-1 forecast window was chosen after inspecting ZYE_0088 phase predictability; the other three mice are subject holdouts.",
            "The forecast model never sees behavioral outcome; its only target is the authors' onset phase half.",
            "The behavioral subset uses the authors' acausal amplitude eligibility through sample 141, so this is a decomposition of their positive, not a causal behavioral analysis.",
            "A positive actual-onset split with a null forecast split would mean the behavior-linked component is not recovered by this simple pre-event phase forecast; it would not prove stimulus reset or leakage uniquely.",
        ],
        "subjects": rows,
        "heldout_aggregate": {
            "mean_phase_forecast_auc_all_trials": float(np.mean(phase_auc)),
            "phase_forecast_auc_above_0_5_subjects": int(np.sum(phase_auc > 0.5)),
            "actual_onset_phase_hit_diff_mean": float(np.mean(actual)),
            "actual_onset_phase_positive_subjects": int(np.sum(actual > 0)),
            "forecast_prestim_phase_hit_diff_mean": float(np.mean(forecast)),
            "forecast_prestim_phase_positive_subjects": int(np.sum(forecast > 0)),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nHELDOUT", json.dumps(result["heldout_aggregate"], indent=2), flush=True)
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
