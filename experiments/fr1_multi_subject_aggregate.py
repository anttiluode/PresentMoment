"""Aggregate independently selected participant-level FR1 PTE calibration results.

Input is a directory tree containing JSON outputs from fr1_multi_subject_pte.py.
The unit of inference here is the participant/session, not the trial.

For each epoch family it reports:

* delta/theta direction index (positive = HIPP->parietal)
* beta direction index (same sign convention)
* frequency contrast delta/theta DI - beta DI
* sign counts
* exact subject-level sign-flip p-values for the mean of each quantity

With a tiny cohort, p-values are coarse and descriptive. The main purpose is to decide
whether the method/data path is stable enough to justify the later state-conditioned
accessibility experiment.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np


def exact_sign_flip_p(values: list[float]) -> float:
    x = np.asarray(values, dtype=np.float64)
    n = len(x)
    if n == 0:
        return float("nan")
    observed = abs(float(np.mean(x)))
    extreme = 0
    total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=n):
        m = abs(float(np.mean(x * np.asarray(signs))))
        extreme += int(m >= observed - 1e-15)
        total += 1
    return extreme / total


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--out", type=Path, default=Path("results/fr1-multi-subject-summary.json"))
    args = p.parse_args()

    paths = sorted(args.root.rglob("*.json"))
    rows = []
    seen = set()
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or "bands" not in data or "selection" not in data:
            continue
        key = (data.get("subject"), data.get("session"))
        if key in seen:
            continue
        seen.add(key)
        rows.append(data)

    if not rows:
        raise RuntimeError(f"no participant JSON outputs found under {args.root}")

    print(f"participants={len(rows)}")
    for row in rows:
        print(
            f"  {row['subject']} ses-{row['session']} "
            f"H={row['selection']['hippocampal']['channel']} "
            f"P={row['selection']['parietal']['channel']} "
            f"({row['selection']['parietal']['class']})"
        )

    summary: dict[str, object] = {
        "n_participants": len(rows),
        "participants": [
            {
                "subject": r["subject"],
                "session": r["session"],
                "hippocampal_channel": r["selection"]["hippocampal"]["channel"],
                "parietal_channel": r["selection"]["parietal"]["channel"],
                "parietal_class": r["selection"]["parietal"]["class"],
            }
            for r in rows
        ],
        "epochs": {},
    }

    for epoch_name in ("successful_encoding", "recall"):
        dt = [
            float(r["bands"]["delta_theta"][epoch_name]["paired_direction_index_mean"])
            for r in rows
        ]
        beta = [
            float(r["bands"]["beta"][epoch_name]["paired_direction_index_mean"])
            for r in rows
        ]
        contrast = [a - b for a, b in zip(dt, beta)]

        epoch_summary = {
            "delta_theta_di": dt,
            "beta_di": beta,
            "delta_theta_minus_beta": contrast,
            "delta_theta_mean": float(np.mean(dt)),
            "beta_mean": float(np.mean(beta)),
            "contrast_mean": float(np.mean(contrast)),
            "delta_theta_positive_count": int(np.count_nonzero(np.asarray(dt) > 0)),
            "beta_negative_count": int(np.count_nonzero(np.asarray(beta) < 0)),
            "contrast_positive_count": int(np.count_nonzero(np.asarray(contrast) > 0)),
            "delta_theta_subject_signflip_p": exact_sign_flip_p(dt),
            "beta_subject_signflip_p": exact_sign_flip_p(beta),
            "contrast_subject_signflip_p": exact_sign_flip_p(contrast),
        }
        summary["epochs"][epoch_name] = epoch_summary

        print(f"\n{epoch_name}")
        print("  delta/theta DI:", " ".join(f"{x:+.4f}" for x in dt))
        print("  beta DI:       ", " ".join(f"{x:+.4f}" for x in beta))
        print("  DT-beta:       ", " ".join(f"{x:+.4f}" for x in contrast))
        print(
            f"  means DT={np.mean(dt):+.4f} beta={np.mean(beta):+.4f} "
            f"contrast={np.mean(contrast):+.4f}"
        )
        print(
            f"  signs DT+ {epoch_summary['delta_theta_positive_count']}/{len(rows)}, "
            f"beta- {epoch_summary['beta_negative_count']}/{len(rows)}, "
            f"contrast+ {epoch_summary['contrast_positive_count']}/{len(rows)}"
        )
        print(
            "  exact sign-flip p: "
            f"DT={epoch_summary['delta_theta_subject_signflip_p']:.4f} "
            f"beta={epoch_summary['beta_subject_signflip_p']:.4f} "
            f"contrast={epoch_summary['contrast_subject_signflip_p']:.4f}"
        )

    print("\nGuardrail")
    print("---------")
    print("This is a small independently selected calibration cohort. It is not intended to")
    print("replace the published large-sample mixed-effects replication. The go/no-go question")
    print("is whether the qualitative frequency-specific feedback structure is stable enough")
    print("for us to condition it on a separate brain-state variable without chasing noise.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
