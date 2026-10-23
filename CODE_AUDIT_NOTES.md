# Code Audit Notes

## Resolved: 39,294 vs 4,486

The counts came from different rules.

`check_duplicates.py` originally counted rows belonging to binary-label-conflicting feature groups using the dataset's native numeric representation. That produced 4,486 affected rows.

`create_splits.py` converts model features to `float32` before hashing and quarantines the union of:
- fingerprints with conflicting binary labels; and
- fingerprints appearing on more than one capture day.

That broader union produced 39,294 quarantined rows.

The cleaned `check_duplicates.py` now prints both native-precision and model-visible float32 audits so the difference can be reproduced directly.

## Split leakage

`create_splits.py` assigns every retained fingerprint to only one experiment group and asserts that a fingerprint cannot cross groups.

`check_float32_leakage.py` independently re-hashes the exact model-visible float32 feature vectors and checks for cross-split duplicates.

These checks address exact duplicate model-input leakage. They do not rule out near-duplicates, correlated flows, dataset artifacts, or day/attack-family confounding.

## Main design limitation

The candidate was built from flows the baseline already classified as highly confident benign.

The later contamination check showed that 36.11% of those selected flows were actually attacks.

However, the baseline itself had 0% Wednesday attack recall. Therefore the main comparative unseen-recall metric had a floor at 0%, making a further degradation impossible to demonstrate.

This is why Experiment 1 is reported as inconclusive rather than as a failed or successful proof.
