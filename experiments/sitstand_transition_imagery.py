#!/usr/bin/env python3
"""Preregistered sit/stand transition-vs-static motor-imagery assay.

See docs/TRANSITION_IMAGERY_GATE.md before changing this file.

The key test is cross-posture generalization:

    train sitting:  transition=mi_sit_std, static=mi_sit_sit
    test standing:  transition=mi_std_sit, static=mi_std_std

and reverse. Because cue direction reverses its label across posture, success cannot be
explained by a fixed up-arrow/down-arrow rule. Sensorimotor features are compared with
an occipital control using the same simple mu/beta relative-bandpower representation
that failed to isolate motor-specific transfer in EEGMMIDB.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


SENSORIMOTOR = (
    "fcz", "fc1", "fc2", "fc3", "fc4",
    "cz", "c1", "c2", "c3", "c4",
    "cpz", "cp1", "cp2", "cp3", "cp4",
)
OCCIPITAL = ("poz", "po3", "po4", "po7", "po8", "o1", "oz", "o2")
BANDS = ((8.0, 13.0), (13.0, 30.0))
BROADBAND = (4.0, 40.0)
WINDOW = (0.5, 3.0)

SITTING = ("mi_sit_std", "mi_sit_sit")   # transition, static
STANDING = ("mi_std_sit", "mi_std_std")  # transition, static


def _pipeline():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.0, solver="liblinear", random_state=0),
    )


def balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    out = []
    for klass in (0, 1):
        mask = y_true == klass
        if mask.any():
            out.append(float(np.mean(y_pred[mask] == klass)))
    return float(np.mean(out)) if out else float("nan")


def bandpower_features(data, sfreq, names, wanted):
    names = [n.lower().strip() for n in names]
    lookup = {n: i for i, n in enumerate(names)}
    present = [n for n in wanted if n in lookup]
    minimum = 5 if wanted is SENSORIMOTOR else 4
    if len(present) < minimum:
        raise RuntimeError(f"Only {len(present)} requested channels found: {present}")

    x = data[:, [lookup[n] for n in present], :]
    x = x - x.mean(axis=-1, keepdims=True)
    win = np.hanning(x.shape[-1])[None, None, :]
    power = np.abs(np.fft.rfft(x * win, axis=-1)) ** 2
    freqs = np.fft.rfftfreq(x.shape[-1], 1.0 / sfreq)
    bb = (freqs >= BROADBAND[0]) & (freqs < BROADBAND[1])
    denom = power[..., bb].mean(axis=-1)
    eps = np.finfo(float).tiny

    pieces = []
    for lo, hi in BANDS:
        mask = (freqs >= lo) & (freqs < hi)
        bp = power[..., mask].mean(axis=-1)
        pieces.append(np.log((bp + eps) / (denom + eps)))
    return np.concatenate(pieces, axis=1), present


def get_condition(ep, name):
    if name not in ep.event_id:
        raise RuntimeError(
            f"Missing condition {name!r}; available={sorted(ep.event_id)}"
        )
    return ep[name].copy().crop(tmin=WINDOW[0], tmax=WINDOW[1]).get_data(copy=True)


def make_domain(ep, pair, wanted):
    transition = get_condition(ep, pair[0])
    static = get_condition(ep, pair[1])
    data = np.concatenate([transition, static], axis=0)
    y = np.concatenate([
        np.ones(len(transition), dtype=int),
        np.zeros(len(static), dtype=int),
    ])
    x, present = bandpower_features(
        data, float(ep.info["sfreq"]), list(ep.ch_names), wanted
    )
    return x, y, present, len(transition), len(static)


def cross_score(train_x, train_y, test_x, test_y):
    model = _pipeline()
    model.fit(train_x, train_y)
    return balanced_accuracy(test_y, model.predict(test_x))


def subject_result(path: Path, subject: str):
    import mne
    mne.set_log_level("ERROR")
    ep = mne.read_epochs(path, preload=True, verbose="ERROR")

    if ep.tmin > WINDOW[0] or ep.tmax < WINDOW[1]:
        raise RuntimeError(
            f"{subject}: requested window {WINDOW} outside epoch [{ep.tmin}, {ep.tmax}]"
        )

    rows = []
    for group, wanted in (("sensorimotor", SENSORIMOTOR), ("occipital", OCCIPITAL)):
        sx, sy, present_s, ns_t, ns_s = make_domain(ep, SITTING, wanted)
        tx, ty, present_t, nt_t, nt_s = make_domain(ep, STANDING, wanted)
        if present_s != present_t:
            raise RuntimeError("Channel group changed across domains")

        sit_to_stand = cross_score(sx, sy, tx, ty)
        stand_to_sit = cross_score(tx, ty, sx, sy)
        rows.append({
            "subject": subject,
            "group": group,
            "n_features": int(sx.shape[1]),
            "n_sit_transition": ns_t,
            "n_sit_static": ns_s,
            "n_stand_transition": nt_t,
            "n_stand_static": nt_s,
            "sit_train_stand_test": sit_to_stand,
            "stand_train_sit_test": stand_to_sit,
            "cross_posture_mean": (sit_to_stand + stand_to_sit) / 2.0,
        })
    return rows


def bootstrap_ci(values, seed=23, n_boot=20000):
    v = np.asarray([x for x in values if np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return [float("nan"), float("nan")]
    rng = np.random.default_rng(seed)
    means = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def signflip_p(values, seed=29, n_perm=50000):
    v = np.asarray([x for x in values if np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return float("nan")
    obs = abs(float(v.mean()))
    rng = np.random.default_rng(seed)
    # Chunk to avoid a large allocation for bigger cohorts.
    ge = 0
    done = 0
    while done < n_perm:
        n = min(5000, n_perm - done)
        signs = rng.choice((-1.0, 1.0), size=(n, len(v)))
        null = np.abs((signs * v[None, :]).mean(axis=1))
        ge += int(np.sum(null >= obs))
        done += n
    return float((1 + ge) / (1 + n_perm))


def summarise(rows, gate=False):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["group"], []).append(row)

    summary = {"n_subjects": len({r["subject"] for r in rows}), "groups": {}}
    for group, rs in grouped.items():
        vals = [float(r["cross_posture_mean"]) for r in rs]
        summary["groups"][group] = {
            "mean": float(np.mean(vals)),
            "median": float(np.median(vals)),
            "bootstrap_mean_95ci": bootstrap_ci(vals, seed=17),
            "n_above_chance": int(np.sum(np.asarray(vals) > 0.5)),
        }

    sm = {r["subject"]: r for r in grouped.get("sensorimotor", [])}
    oc = {r["subject"]: r for r in grouped.get("occipital", [])}
    common = sorted(set(sm) & set(oc))
    diffs = [
        float(sm[s]["cross_posture_mean"]) - float(oc[s]["cross_posture_mean"])
        for s in common
    ]
    ci = bootstrap_ci(diffs, seed=23)
    p = signflip_p(diffs, seed=29)
    mean_d = float(np.mean(diffs)) if diffs else float("nan")
    sm_mean = summary["groups"].get("sensorimotor", {}).get("mean", float("nan"))

    summary["paired_sensorimotor_minus_occipital"] = {
        "n": len(diffs),
        "mean": mean_d,
        "bootstrap_mean_95ci": ci,
        "signflip_p_two_sided": p,
        "n_positive": int(np.sum(np.asarray(diffs) > 0)) if diffs else 0,
    }

    if gate:
        passed = (
            np.isfinite(sm_mean) and sm_mean > 0.55
            and np.isfinite(mean_d) and mean_d > 0.03
            and np.isfinite(ci[0]) and ci[0] > 0
            and np.isfinite(p) and p < 0.05
        )
        summary["verdict"] = (
            "SENSORIMOTOR_TRANSITION_ADVANTAGE"
            if passed else "NO_CLEAN_TRANSITION_ADVANTAGE"
        )
    else:
        summary["verdict"] = "EXPLORATION_ONLY_NO_GATE"

    summary["frozen_window_s"] = list(WINDOW)
    summary["warning"] = (
        "A positive held-out result means cross-posture transition-vs-static imagery "
        "is more decodable over the frozen sensorimotor feature set than the occipital "
        "control. It does not establish consciousness, literal simulation, or free will."
    )
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--subjects", nargs="+", required=True)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    args = ap.parse_args()

    rows = []
    for subject in args.subjects:
        path = args.data_dir / f"{subject}.fif"
        if not path.exists():
            raise FileNotFoundError(path)
        print(f"{subject}: {path}", flush=True)
        rs = subject_result(path, subject)
        rows.extend(rs)
        for r in rs:
            print(
                f"  {r['group']:12s} "
                f"sit->stand={r['sit_train_stand_test']:.3f} "
                f"stand->sit={r['stand_train_sit_test']:.3f} "
                f"mean={r['cross_posture_mean']:.3f}",
                flush=True,
            )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = summarise(rows, gate=args.gate)
    args.out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
