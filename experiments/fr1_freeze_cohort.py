"""Freeze an outcome-blind FR1 calibration cohort from metadata only.

This script exists because an earlier permissive anatomy matcher accidentally allowed
``angular`` to match ``parstriangularis``.  Some connectivity outcomes from that invalid
screen had already been seen before the bug was caught, so the replacement cohort must
not be hand-selected.

The frozen rule is specified BEFORE any replacement-cohort PTE is computed:

1. inspect subjects in lexical OpenNeuro order;
2. require a strict bipolar hippocampal pair (both contacts explicitly hippocampal);
3. require a strict bipolar parietal pair (both contacts same target class:
   angular / supramarginal / PCC / precuneus), excluding cortical white matter;
4. require hippocampal and parietal pairs in the SAME hemisphere;
5. keep at most one session per subject: the smallest qualifying bipolar EDF;
6. sort qualifying subjects by bipolar EDF size, then subject/session name;
7. take the first N subjects.

No neural signal is downloaded and no connectivity result is read.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from fr1_strict_pair_screen import (
    DATASET,
    list_objects,
    pair_candidates,
    read_tsv,
    session_prefix_from_key,
)


def contact_hemi(contact: dict) -> str | None:
    """Infer hemisphere from explicit anatomy string or contact name."""
    name = str(contact.get("name", "")).upper()
    anatomy = json.dumps(contact.get("anatomy", {})).lower()
    if "left" in anatomy:
        return "L"
    if "right" in anatomy:
        return "R"
    if name.startswith("L"):
        return "L"
    if name.startswith("R"):
        return "R"
    return None


def pair_hemi(pair: dict) -> str | None:
    a = contact_hemi(pair["contact_a"])
    b = contact_hemi(pair["contact_b"])
    return a if a is not None and a == b else None


def same_hemi_combos(hip_pairs: list[dict], par_pairs: list[dict]) -> list[tuple[dict, dict, str]]:
    out = []
    for hip in hip_pairs:
        hh = pair_hemi(hip)
        if hh is None:
            continue
        for par in par_pairs:
            ph = pair_hemi(par)
            if ph == hh:
                out.append((hip, par, hh))
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max-subjects", type=int, default=120)
    p.add_argument("--n", type=int, default=6)
    p.add_argument("--out", default="results/fr1-frozen-cohort.json")
    args = p.parse_args()

    root = list_objects(f"{DATASET}/", delimiter="/")
    subjects = sorted(
        x for x in root["prefixes"] if re.search(r"/sub-[^/]+/$", x)
    )[: args.max_subjects]

    best_by_subject: dict[str, dict] = {}
    inspected_sessions = 0

    for subject_prefix in subjects:
        listing = list_objects(subject_prefix, max_keys=1000)
        by_session: dict[str, list[tuple[str, int]]] = {}
        for key, size in listing["keys"]:
            sp = session_prefix_from_key(key)
            if sp:
                by_session.setdefault(sp, []).append((key, size))

        for sp, objects in sorted(by_session.items()):
            electrode_files = [k for k, _ in objects if k.endswith("electrodes.tsv")]
            bipolar_files = [k for k, _ in objects if k.endswith("acq-bipolar_channels.tsv")]
            edfs = [(k, s) for k, s in objects if k.endswith("acq-bipolar_ieeg.edf")]
            events = [k for k, _ in objects if k.endswith("events.tsv")]
            if not (electrode_files and bipolar_files and edfs and events):
                continue
            inspected_sessions += 1

            electrodes = read_tsv(electrode_files[0])
            bipolar = read_tsv(bipolar_files[0])
            hip_pairs, par_pairs = pair_candidates(electrodes, bipolar)
            combos = same_hemi_combos(hip_pairs, par_pairs)
            if not combos:
                continue

            subject = sp.split("/")[1].removeprefix("sub-")
            session = sp.split("/")[2].removeprefix("ses-")
            edf_key, edf_size = min(edfs, key=lambda x: x[1])

            row = {
                "subject": subject,
                "session": session,
                "bipolar_edf": edf_key,
                "bipolar_edf_mib": edf_size / (1024 ** 2),
                "events_tsv": events[0],
                "n_hippocampal_pairs": len(hip_pairs),
                "n_parietal_pairs": len(par_pairs),
                "n_same_hemi_combos": len(combos),
                "hemispheres": sorted(set(h for _, _, h in combos)),
                "hippocampal_channels": sorted(set(h["channel"] for h, _, _ in combos)),
                "parietal_channels": sorted(
                    set((par["channel"], par["class"]) for _, par, _ in combos)
                ),
            }

            old = best_by_subject.get(subject)
            if old is None or (row["bipolar_edf_mib"], row["session"]) < (
                old["bipolar_edf_mib"], old["session"]
            ):
                best_by_subject[subject] = row

    eligible = sorted(
        best_by_subject.values(),
        key=lambda r: (r["bipolar_edf_mib"], r["subject"], r["session"]),
    )
    frozen = eligible[: args.n]

    payload = {
        "rule": "strict gray-matter same-hemi; one smallest session/subject; then smallest EDF first",
        "screen_version": "token-exact-gray-matter-v2",
        "subjects_scanned": len(subjects),
        "sessions_inspected": inspected_sessions,
        "eligible_subjects": len(eligible),
        "n_requested": args.n,
        "frozen_cohort": frozen,
        "next_eligible": eligible[args.n : args.n + 8],
    }

    print("Outcome-blind frozen FR1 cohort")
    print("rule:", payload["rule"])
    print(f"eligible subjects={len(eligible)}")
    for i, row in enumerate(frozen, 1):
        print(
            f"{i}. {row['subject']} ses-{row['session']} "
            f"{row['bipolar_edf_mib']:.1f} MiB hemi={row['hemispheres']}"
        )
        print("   HIP:", row["hippocampal_channels"][:8])
        print("   PAR:", row["parietal_channels"][:10])

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
