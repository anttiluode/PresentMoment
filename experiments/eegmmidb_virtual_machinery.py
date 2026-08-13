#!/usr/bin/env python3
"""Test whether executed-movement geometry transfers to imagined movement.

This experiment uses the public PhysioNet EEG Motor Movement/Imagery Database
(EEGMMIDB).  The deliberately modest question is whether a classifier/contrast
learned from *executed* left-vs-right hand movement remains informative when the
same participant only imagines the movement, and vice versa.

This is NOT a consciousness test and it is NOT by itself evidence for a general
"simulation" theory.  The task cue is lateralized (left/right target on screen),
so the dataset has a built-in visual confound.  We therefore report the same
transfer metrics in a sensorimotor channel set and an occipital control set.  A
useful result requires sensorimotor transfer to exceed the occipital control; if
it does not, the safest interpretation is cue/shared-task structure rather than
reinstated motor machinery.

Dataset
-------
PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0
https://physionet.org/content/eegmmidb/1.0.0/
DOI: 10.13026/C28G6P

Runs used
---------
3, 7, 11   executed left vs right fist
4, 8, 12   imagined left vs right fist

Outputs one row per subject and channel group plus an aggregate JSON summary.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np


EXECUTION_RUNS = (3, 7, 11)
IMAGERY_RUNS = (4, 8, 12)

# Keep the primary test over central/frontocentral/parietocentral electrodes.
SENSORIMOTOR_CHANNELS = (
    "FC3", "FC1", "FCz", "FC2", "FC4",
    "C3", "C1", "Cz", "C2", "C4",
    "CP3", "CP1", "CPz", "CP2", "CP4",
)

# Negative-control-ish region for the lateral visual cue confound.  It is not a
# perfect control: visual/task information can propagate broadly, which is why
# a null sensorimotor-minus-occipital result should kill the strong story.
OCCIPITAL_CHANNELS = (
    "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
)

BANDS = ((8.0, 13.0), (13.0, 30.0))
BROADBAND = (4.0, 40.0)


def parse_subjects(text: str) -> list[int]:
    """Parse '1-12,20,22-24' into sorted unique subject IDs."""
    out: set[int] = set()
    for chunk in text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            lo, hi = int(a), int(b)
            if hi < lo:
                lo, hi = hi, lo
            out.update(range(lo, hi + 1))
        else:
            out.add(int(chunk))
    subjects = sorted(out)
    if not subjects:
        raise ValueError("No subjects selected")
    bad = [s for s in subjects if not 1 <= s <= 109]
    if bad:
        raise ValueError(f"EEGMMIDB subject IDs must be 1..109; got {bad}")
    return subjects


def _normalise_channel_name(name: str) -> str:
    # EEGMMIDB EDF labels sometimes contain trailing dots/spaces.  MNE's
    # eegbci.standardize() handles these, but keep this as a second guard.
    return name.strip().rstrip(".")


def load_task_epochs(subject: int, runs: Iterable[int], cache_dir: Path):
    """Load task epochs and retain run identity for leave-one-run-out tests."""
    import mne
    from mne.datasets import eegbci

    mne.set_log_level("ERROR")
    paths = eegbci.load_data(
        subject,
        list(runs),
        path=str(cache_dir),
        update_path=False,
        verbose=False,
    )

    all_data: list[np.ndarray] = []
    all_labels: list[np.ndarray] = []
    all_run_ids: list[np.ndarray] = []
    channel_names: list[str] | None = None
    sfreq: float | None = None

    for run, path in zip(runs, paths):
        raw = mne.io.read_raw_edf(path, preload=True, verbose="ERROR")
        eegbci.standardize(raw)
        raw.rename_channels({ch: _normalise_channel_name(ch) for ch in raw.ch_names})
        raw.pick_types(eeg=True, exclude=[])
        raw.set_eeg_reference("average", projection=False, verbose="ERROR")

        events, _ = mne.events_from_annotations(
            raw,
            event_id={"T1": 1, "T2": 2},
            verbose="ERROR",
        )
        epochs = mne.Epochs(
            raw,
            events,
            event_id={"left": 1, "right": 2},
            tmin=0.5,
            tmax=3.5,
            baseline=None,
            preload=True,
            reject_by_annotation=True,
            verbose="ERROR",
        )

        data = epochs.get_data(copy=True)  # epochs x channels x time
        labels = epochs.events[:, -1].astype(int) - 1  # left=0, right=1
        if data.shape[0] == 0:
            raise RuntimeError(f"Subject {subject} run {run}: no usable task epochs")

        names = [_normalise_channel_name(ch) for ch in epochs.ch_names]
        if channel_names is None:
            channel_names = names
            sfreq = float(epochs.info["sfreq"])
        elif names != channel_names:
            raise RuntimeError(f"Subject {subject}: channel order changed across runs")

        all_data.append(data)
        all_labels.append(labels)
        all_run_ids.append(np.full(len(labels), int(run), dtype=int))

    assert channel_names is not None and sfreq is not None
    return (
        np.concatenate(all_data, axis=0),
        np.concatenate(all_labels, axis=0),
        np.concatenate(all_run_ids, axis=0),
        channel_names,
        sfreq,
    )


def bandpower_features(
    data: np.ndarray,
    channel_names: list[str],
    sfreq: float,
    wanted_channels: Iterable[str],
) -> tuple[np.ndarray, list[str]]:
    """Relative log band-power features for a named electrode group."""
    index = {name: i for i, name in enumerate(channel_names)}
    present = [ch for ch in wanted_channels if ch in index]
    if len(present) < 3:
        raise RuntimeError(
            f"Only {len(present)} requested channels found: {present}; "
            f"available sample={channel_names[:12]}"
        )
    x = data[:, [index[ch] for ch in present], :]
    x = x - x.mean(axis=-1, keepdims=True)

    win = np.hanning(x.shape[-1])[None, None, :]
    spec = np.fft.rfft(x * win, axis=-1)
    power = np.abs(spec) ** 2
    freqs = np.fft.rfftfreq(x.shape[-1], d=1.0 / sfreq)

    bb_mask = (freqs >= BROADBAND[0]) & (freqs < BROADBAND[1])
    broadband = power[..., bb_mask].mean(axis=-1)
    eps = np.finfo(float).tiny

    pieces = []
    feature_names = []
    for lo, hi in BANDS:
        mask = (freqs >= lo) & (freqs < hi)
        bp = power[..., mask].mean(axis=-1)
        rel = np.log((bp + eps) / (broadband + eps))
        pieces.append(rel)
        feature_names.extend([f"{ch}:{lo:g}-{hi:g}Hz" for ch in present])
    return np.concatenate(pieces, axis=1), feature_names


def _pipeline():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.0, solver="liblinear", random_state=0),
    )


def balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    recalls = []
    for klass in (0, 1):
        mask = y_true == klass
        if mask.any():
            recalls.append(float(np.mean(y_pred[mask] == klass)))
    return float(np.mean(recalls)) if recalls else float("nan")


def leave_one_run_out(x: np.ndarray, y: np.ndarray, run_ids: np.ndarray) -> float:
    scores = []
    for run in sorted(np.unique(run_ids)):
        test = run_ids == run
        train = ~test
        if len(np.unique(y[train])) < 2 or len(np.unique(y[test])) < 2:
            continue
        model = _pipeline()
        model.fit(x[train], y[train])
        scores.append(balanced_accuracy(y[test], model.predict(x[test])))
    return float(np.mean(scores)) if scores else float("nan")


def cross_domain(train_x, train_y, test_x, test_y) -> float:
    model = _pipeline()
    model.fit(train_x, train_y)
    return balanced_accuracy(test_y, model.predict(test_x))


def contrast_cosine(exec_x, exec_y, img_x, img_y) -> float:
    """Cosine alignment of left-right contrast vectors in common coordinates."""
    pooled = np.vstack([exec_x, img_x])
    mu = pooled.mean(axis=0)
    sd = pooled.std(axis=0)
    sd[sd < 1e-12] = 1.0
    ex = (exec_x - mu) / sd
    im = (img_x - mu) / sd
    ve = ex[exec_y == 1].mean(axis=0) - ex[exec_y == 0].mean(axis=0)
    vi = im[img_y == 1].mean(axis=0) - im[img_y == 0].mean(axis=0)
    denom = float(np.linalg.norm(ve) * np.linalg.norm(vi))
    if denom == 0:
        return float("nan")
    return float(np.dot(ve, vi) / denom)


def signflip_p(values: Iterable[float], seed: int = 0, n_perm: int = 20000) -> float:
    """Two-sided sign-flip test of a paired effect against zero."""
    v = np.asarray([x for x in values if np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return float("nan")
    obs = abs(float(np.mean(v)))
    rng = np.random.default_rng(seed)
    signs = rng.choice((-1.0, 1.0), size=(n_perm, len(v)))
    null = np.abs((signs * v[None, :]).mean(axis=1))
    return float((1 + np.sum(null >= obs)) / (n_perm + 1))


def bootstrap_ci(values: Iterable[float], seed: int = 0, n_boot: int = 10000):
    v = np.asarray([x for x in values if np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return [float("nan"), float("nan")]
    rng = np.random.default_rng(seed)
    samples = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(axis=1)
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def summarise(rows: list[dict]) -> dict:
    by_group: dict[str, list[dict]] = {}
    for row in rows:
        by_group.setdefault(row["group"], []).append(row)

    summary: dict[str, object] = {
        "n_subjects": len(sorted({int(r["subject"]) for r in rows})),
        "groups": {},
    }
    for group, rs in by_group.items():
        metrics = {}
        for key in (
            "within_execution",
            "within_imagery",
            "exec_to_imagery",
            "imagery_to_exec",
            "transfer_mean",
            "contrast_cosine",
        ):
            vals = [float(r[key]) for r in rs if math.isfinite(float(r[key]))]
            metrics[key] = {
                "mean": float(np.mean(vals)) if vals else float("nan"),
                "median": float(np.median(vals)) if vals else float("nan"),
                "bootstrap_mean_95ci": bootstrap_ci(vals, seed=17),
            }
        summary["groups"][group] = metrics

    # Paired sensorimotor - occipital is the main anti-confound contrast.
    sm = {int(r["subject"]): r for r in by_group.get("sensorimotor", [])}
    oc = {int(r["subject"]): r for r in by_group.get("occipital", [])}
    common = sorted(set(sm) & set(oc))
    paired = {}
    for key in ("transfer_mean", "contrast_cosine"):
        diffs = [float(sm[s][key]) - float(oc[s][key]) for s in common]
        paired[key] = {
            "n": len(diffs),
            "mean_sensorimotor_minus_occipital": float(np.mean(diffs)) if diffs else float("nan"),
            "bootstrap_mean_95ci": bootstrap_ci(diffs, seed=23),
            "signflip_p_two_sided": signflip_p(diffs, seed=29),
            "n_positive": int(np.sum(np.asarray(diffs) > 0)) if diffs else 0,
        }
    summary["paired_sensorimotor_minus_occipital"] = paired

    # Conservative interpretation gate.  It is intentionally not a discovery
    # threshold; it merely stops us from narrating a cue-driven result as motor
    # reinstatement.
    transfer = paired.get("transfer_mean", {})
    ci = transfer.get("bootstrap_mean_95ci", [float("nan"), float("nan")])
    effect = float(transfer.get("mean_sensorimotor_minus_occipital", float("nan")))
    if np.isfinite(effect) and effect > 0 and np.isfinite(ci[0]) and ci[0] > 0:
        verdict = "sensorimotor_transfer_exceeds_occipital_control"
    else:
        verdict = "NO_CLEAN_SENSORIMOTOR_ADVANTAGE"
    summary["interpretation_gate"] = verdict
    summary["warning"] = (
        "EEGMMIDB left/right labels are also left/right visual target locations. "
        "Even a positive sensorimotor result demonstrates shared task/motor geometry, "
        "not a general theory of internal simulation or subjectivity."
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", default="1-12")
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/eegmmidb"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/eegmmidb_virtual_machinery.csv"))
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/eegmmidb_virtual_machinery.json"))
    args = ap.parse_args()

    subjects = parse_subjects(args.subjects)
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    groups = {
        "sensorimotor": SENSORIMOTOR_CHANNELS,
        "occipital": OCCIPITAL_CHANNELS,
    }

    for subject in subjects:
        print(f"subject {subject:03d}: loading execution", flush=True)
        ex_data, ex_y, ex_runs, names, sfreq = load_task_epochs(
            subject, EXECUTION_RUNS, args.cache_dir
        )
        print(f"subject {subject:03d}: loading imagery", flush=True)
        im_data, im_y, im_runs, names2, sfreq2 = load_task_epochs(
            subject, IMAGERY_RUNS, args.cache_dir
        )
        if names != names2 or sfreq != sfreq2:
            raise RuntimeError(f"Subject {subject}: execution/imagery recording mismatch")

        for group, wanted in groups.items():
            ex_x, feat_names = bandpower_features(ex_data, names, sfreq, wanted)
            im_x, _ = bandpower_features(im_data, names, sfreq, wanted)
            e2i = cross_domain(ex_x, ex_y, im_x, im_y)
            i2e = cross_domain(im_x, im_y, ex_x, ex_y)
            row = {
                "subject": subject,
                "group": group,
                "n_features": len(feat_names),
                "n_execution_epochs": len(ex_y),
                "n_imagery_epochs": len(im_y),
                "within_execution": leave_one_run_out(ex_x, ex_y, ex_runs),
                "within_imagery": leave_one_run_out(im_x, im_y, im_runs),
                "exec_to_imagery": e2i,
                "imagery_to_exec": i2e,
                "transfer_mean": (e2i + i2e) / 2.0,
                "contrast_cosine": contrast_cosine(ex_x, ex_y, im_x, im_y),
            }
            rows.append(row)
            print(
                f"  {group:12s} within(exec/img)="
                f"{row['within_execution']:.3f}/{row['within_imagery']:.3f} "
                f"transfer={row['transfer_mean']:.3f} "
                f"cos={row['contrast_cosine']:.3f}",
                flush=True,
            )

    fieldnames = list(rows[0].keys())
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    result = summarise(rows)
    args.out_json.write_text(json.dumps(result, indent=2, allow_nan=True), encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
