#!/usr/bin/env python3
"""Robust sidecar wrapper for fr1_lagged_accessibility.py.

Reuses the S3 key resolver already validated by fr1_multi_subject_pte_v2.py. This
changes only OpenNeuro sidecar discovery; cohort, anatomy selection, estimator, null,
lags, and statistics remain unchanged.
"""
import fr1_multi_subject_pte as anatomy
from fr1_multi_subject_pte_v2 import robust_remote_tsv
import fr1_lagged_accessibility as probe

anatomy.remote_tsv = robust_remote_tsv

if __name__ == "__main__":
    probe.main()
