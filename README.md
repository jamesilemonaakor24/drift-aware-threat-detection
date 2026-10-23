# Drift-Aware Threat Detection

## Overview

This repository documents an exploratory machine-learning intrusion-detection experiment using the CIC-IDS2017 dataset.

The experiment asked whether a model update could pass a safety audit based on older traffic while still performing poorly on newer traffic. The aim was to test a specific failure mechanism honestly, not to force a positive result.

## Research Question

Can an intrusion-detection model pass a safety check using older reference data but perform worse on newer network traffic?

## Dataset and Experimental Setup

Dataset: CIC-IDS2017 MachineLearningCVE CSV files.

For Experiment 1:

- Monday and Tuesday were treated as earlier traffic.
- Wednesday was treated as a newer capture session.
- Monday/Tuesday were divided into `training`, `old_audit`, and `known_test`.
- Wednesday was divided into `update`, `recent_audit`, and `blind_test`.
- The Random Forest baseline was trained only on Monday/Tuesday training data.
- Wednesday true labels were not used to train the candidate model.

This is a cross-session experiment. It is **not** a real-time streaming deployment, because the CSV files do not provide per-flow timestamps suitable for reconstructing a continuous timeline.

## Data Preparation

The raw CIC-IDS2017 files were audited before modelling.

The preprocessing pipeline:

- strips whitespace from column names;
- standardises label text;
- replaces infinite values with missing values;
- removes rows containing non-finite values;
- creates a binary target (`0 = benign`, `1 = attack`);
- preserves the original source-file name.

After preprocessing:

- original flows: 2,830,743;
- rows removed for non-finite values: 2,867;
- remaining flows: 2,827,876.

Duplicate rows were not deleted globally because identical feature rows do not necessarily prove that two rows are the same real network event.

## Duplicate and Leakage Controls

The experiment used feature fingerprints to reduce duplicate-feature leakage across experimental groups.

Two different checks were used and should not be confused:

1. `check_duplicates.py` originally reported **4,486 rows** belonging to binary-label-conflicting feature groups under the dataset's native numeric representation.
2. `create_splits.py` quarantined **39,294 rows** using the union of:
   - model-visible `float32` feature fingerprints with conflicting binary labels; and
   - model-visible `float32` feature fingerprints appearing across different capture days.

The 4,486 and 39,294 counts therefore measure different things and are not expected to match.

The final split-generation logic keeps identical model-visible feature fingerprints in only one experimental group. `check_float32_leakage.py` is provided to verify this explicitly.

## Final Experiment Groups

| Group | Records |
|---|---:|
| training | 666,311 |
| old_audit | 191,282 |
| known_test | 99,815 |
| update | 405,581 |
| recent_audit | 139,372 |
| blind_test | 124,877 |

Total retained: 1,627,238  
Quarantined: 39,294

## Baseline Model

Model: Random Forest

Training data:

- Monday and Tuesday `training` groups only;
- 666,311 records;
- 656,912 benign;
- 9,399 attacks.

Known-test results:

- test records: 99,815;
- false positives: 1;
- missed attacks: 0;
- attacks detected: 1,217/1,217;
- attack recall: 100%;
- FTP-Patator: 657/657;
- SSH-Patator: 560/560.

These strong numbers apply only to the held-out Monday/Tuesday attack families represented in the earlier sessions. They should not be interpreted as proof of real-world generalisation.

## Candidate Update

The frozen baseline model scored the Wednesday `update` group.

Flows predicted as benign with at least 99% confidence were eligible for pseudo-labelling. A fixed random sample of 20,000 eligible flows was then labelled as benign and added to the original training data to train a separate candidate model.

No Wednesday true labels were used during candidate training.

### Contamination Check

After the candidate had already been created, the true Wednesday labels were opened for analysis of the selected pseudo-benign update set.

Of 20,000 selected flows:

- actually benign: 12,778;
- actually attacks: 7,222;
- contamination rate: **36.11%**.

Attack classes incorrectly treated as benign included:

- DoS Hulk: 6,733;
- DoS GoldenEye: 341;
- DoS Slowhttptest: 122;
- DoS slowloris: 26.

This demonstrates that very high model confidence did not guarantee safe pseudo-labelling under the changed Wednesday traffic.

## Safety-Audit Result

### Historical audit

The candidate and baseline were compared on 191,282 Monday/Tuesday `old_audit` records.

Both models produced:

- false positives: 0;
- missed attacks: 2;
- attacks detected: 3,214;
- attack recall: 99.94%.

Under the pre-specified comparative thresholds, the historical audit **approved** the candidate because it did not perform worse than the frozen baseline on the old audit data.

### Wednesday evaluation

The later Wednesday evaluation did **not** establish the original harmful-update hypothesis.

Both the baseline and candidate had 0% recall on the Wednesday attack traffic examined. Because the baseline was already at a 0% recall floor, the candidate could not show a further recall decrease on that metric.

Therefore:

- the experiment **did demonstrate severe pseudo-label contamination** under distribution shift;
- it **did not demonstrate that the candidate update became measurably more harmful than the baseline** under the pre-specified comparative rule;
- the harmful-update hypothesis for Experiment 1 is **inconclusive**.

This distinction is intentional. Negative or inconclusive results are part of the research process.

## Main Interpretation

Experiment 1 exposed a design limitation that is itself important for future work:

> A relative safety rule can be uninformative when the reference model already fails completely on the new attack distribution.

It also showed that a model can be highly confident while assigning incorrect pseudo-labels under changed traffic.

The experiment does **not** prove that outdated audits generally approve harmful model updates, and it does **not** establish a novel method.

## Limitations

- CIC-IDS2017 day blocks confound capture day with attack-family changes.
- The CSV files do not provide a reliable row-level timeline for a real streaming experiment.
- The Wednesday groups are held-out samples from one capture day, not successive verified deployment windows.
- The baseline had 0% recall on the new Wednesday attacks, creating a floor effect for the harmful-update comparison.
- The 200-record recent-audit script is an exploratory pilot and is too small for strong statements about very low false-positive rates.
- CIC-IDS2017 contains duplicate-feature and conflicting-label artifacts that require careful handling.
- The current experiment does not test explainability.

## Research Integrity / Next Step

The Wednesday blind evaluation has already been consumed for Experiment 1. It should not be reused as a fresh blind test after redesigning the hypothesis or candidate update.

A follow-up experiment should use previously untouched data or a new experimental split, pre-specify its metrics and thresholds, and avoid the 0%-recall floor by choosing a baseline/target setting where deterioration is actually measurable.

## Repository Structure

```text
drift-aware-threat-detection/
├── src/
│   ├── inspect_data.py
│   ├── preprocess_data.py
│   ├── test_setup.py
│   └── verify_processed_data.py
├── experiments/
│   ├── experiment_protocol.md
│   ├── create_splits.py
│   ├── check_duplicates.py
│   ├── check_float32_leakage.py
│   ├── train_baseline.py
│   ├── test_baseline.py
│   ├── train_candidate.py
│   ├── audit_old_model.py
│   ├── audit_recent_model.py
│   ├── evaluate_blind_test.py
│   └── check_update_contamination.py
├── .gitignore
├── README.md
└── requirements.txt
```

Raw and processed CIC-IDS2017 data are intentionally excluded from the repository.

## Author

**James Ilemona Akor**

Cybersecurity and machine-learning research experiment.

## Experiment 2 follow-up
An exploratory follow-up is included in `experiments/experiment2_protocol.md`. It addresses Experiment 1's 0%-recall floor by first giving the model a small verified Wednesday adaptation seed, then testing the same confidence-based pseudo-labelling update on a separate held-out Wednesday group. Because Wednesday labels were already revealed in Experiment 1, this follow-up is explicitly exploratory rather than a new blind confirmation.
