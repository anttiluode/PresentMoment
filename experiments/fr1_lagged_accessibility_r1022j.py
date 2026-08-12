#!/usr/bin/env python3
"""Run fr1_lagged_accessibility on the already-frozen R1022J anatomical pair.

The generic selector's OpenNeuro sidecar URL does not resolve for this older session.
R1022J's pair was selected and documented before this hypothesis existed:
  HIPP: LB2-LB3 (left DG/CA1)
  PAR:  LH11-LH12 (left angular gyrus)
This wrapper removes only metadata plumbing; it does not change the analysis.
"""
import fr1_lagged_accessibility as probe


def frozen_pair(subject: str, session: str):
    if subject != "R1022J" or str(session) != "0":
        raise ValueError("This wrapper is intentionally only for frozen R1022J ses-0")
    return {
        "hippocampal": {
            "channel": "LB2-LB3",
            "hemisphere": "L",
            "selection_note": "frozen before lagged-accessibility hypothesis; DG/CA1 bipolar pair",
        },
        "parietal": {
            "channel": "LH11-LH12",
            "hemisphere": "L",
            "class": "angular",
            "selection_note": "frozen before lagged-accessibility hypothesis; left angular bipolar pair",
        },
        "selection_source": "prior R1022J FR1 calibration",
    }


probe.select_pair = frozen_pair

if __name__ == "__main__":
    probe.main()
