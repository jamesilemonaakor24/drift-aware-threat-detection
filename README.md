# Drift-Aware Threat Detection

**Author:** James Ilemona Akor  
**Project type:** Exploratory machine-learning intrusion-detection research using CIC-IDS2017.  
**Human participants:** None. This repository uses only network-traffic data and does not contain human-participant research.

## At a glance

This project asks whether a model update can appear safe under older audit data while behaving differently on newer traffic. It was designed to test the hypothesis honestly, including reporting negative and inconclusive results.

- **Experiment 1:** The harmful-update hypothesis was **inconclusive** because both the baseline and candidate had 0% recall on the Wednesday attack traffic, creating a floor effect. The pseudo-labelled update set nevertheless contained **7,222 attacks among 20,000 selected flows (36.11% contamination)**.
- **Experiment 2:** After giving the baseline a small verified Wednesday adaptation seed, the comparison became measurable. The candidate's attack recall changed from **98.39% to 97.65% (-0.74 percentage points)** and did **not** cross the predefined harm limits.
- The project therefore does **not** claim that harmful model updates were demonstrated. It documents what the experiments did and did not establish.

Full verified outcomes are in [`RESULTS.md`](RESULTS.md). Reproduction instructions are in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Research Question

Can an intrusion-detection model pass a safety check using older reference data but perform worse on newer network traffic?

## Dataset and Experimental Setup

Dataset: **CIC-IDS2017 MachineLearningCVE / MachineLearningCSV files**.

The original dataset is published by the Canadian Institute for Cybersecurity, University of New Brunswick:

https://www.unb.ca/cic/datasets/ids-2017.html

Raw and processed dataset files are intentionally excluded from this repository.

For Experiment 1:

- Monday and Tuesday were treated as earlier traffic.
- Wednesday was treated as a newer capture session.
- Monday/Tuesday were divided into `training`, `old_audit`, and `known_test`.
- Wednesday was divided into `update`, `recent_audit`, and `blind_test`.
- The Random Forest baseline was trained only on Monday/Tuesday training data.
- Wednesday true labels were not used to train the candidate model.

This is a **cross-session experiment**, not a real-time streaming deployment. The MachineLearningCVE CSV files used here do not provide the row-level temporal information required to reconstruct a continuous deployment timeline.

## Data Preparation

The preprocessing pipeline:

- strips whitespace from column names;
- standardises label text;
- replaces infinite values with missing values;
- removes rows containing non-finite values;
- creates a binary target (`0 = benign`, `1 = attack`);
- preserves the original source-file name.

After preprocessing:

- original flows: **2,830,743**;
- rows removed for non-finite values: **2,867**;
- remaining flows: **2,827,876**.

Duplicate rows were not deleted globally because identical feature rows do not necessarily prove that two rows represent the same real network event.

## Duplicate and Leakage Controls

The experiment used feature fingerprints to reduce duplicate-feature leakage across experimental groups.

Two checks should not be confused:

1. `check_duplicates.py` originally reported **4,486 rows** belonging to binary-label-conflicting feature groups under the dataset's native numeric representation.
2. `create_splits.py` quarantined **39,294 rows** using the union of:
   - model-visible `float32` feature fingerprints with conflicting binary labels; and
   - model-visible `float32` feature fingerprints appearing across different capture days.

The 4,486 and 39,294 counts measure different things and are not expected to match.

The final split-generation logic keeps identical model-visible feature fingerprints in only one experimental group. `check_float32_leakage.py` verifies this explicitly.

## Final Experiment 1 Groups

| Group | Records |
|---|---:|
| training | 666,311 |
| old_audit | 191,282 |
| known_test | 99,815 |
| update | 405,581 |
| recent_audit | 139,372 |
| blind_test | 124,877 |

Total retained: **1,627,238**  
Quarantined: **39,294**

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

These strong numbers apply only to held-out Monday/Tuesday attack families represented in the earlier sessions. They should not be interpreted as proof of real-world generalisation.

## Candidate Update

The frozen baseline model scored the Wednesday `update` group.

Flows predicted as benign with at least 99% confidence were eligible for pseudo-labelling. A fixed random sample of up to 20,000 eligible flows was labelled as benign and added to the original training data to train a separate candidate model.

No Wednesday true labels were used during candidate training.

### Contamination Check

After the candidate had already been created, the true Wednesday labels were opened to analyse the selected pseudo-benign update set.

Of **20,000 selected flows**:

- actually benign: 12,778;
- actually attacks: 7,222;
- contamination rate: **36.11%**.

Attack classes incorrectly treated as benign included:

- DoS Hulk: 6,733;
- DoS GoldenEye: 341;
- DoS Slowhttptest: 122;
- DoS slowloris: 26.

This demonstrates that very high model confidence did not guarantee safe pseudo-labelling under the changed Wednesday traffic.

## Experiment 1 Outcome

### Historical audit

The candidate and baseline were compared on 191,282 Monday/Tuesday `old_audit` records.

Both models produced:

- false positives: 0;
- missed attacks: 2;
- attacks detected: 3,214;
- attack recall: 99.94%.

Under the predefined comparative thresholds, the historical audit approved the candidate because it did not perform worse than the frozen baseline on the old audit data.

### Wednesday evaluation

The later Wednesday evaluation did **not** establish the original harmful-update hypothesis.

Both the baseline and candidate had 0% recall on the Wednesday attack traffic examined. Because the baseline was already at a 0% recall floor, the candidate could not show a further recall decrease on that metric.

Therefore:

- Experiment 1 **did demonstrate severe pseudo-label contamination** under distribution shift;
- it **did not demonstrate that the candidate became measurably more harmful than the baseline** under the predefined comparative rule;
- the harmful-update hypothesis for Experiment 1 is **inconclusive**.

Negative or inconclusive results are part of the research process.

## Experiment 2 Follow-up

Experiment 2 is an **exploratory follow-up**, not a new project-level blind confirmation. Wednesday labels had already been revealed during Experiment 1.

The redesign first gave the model a small verified Wednesday adaptation seed, then tested the same confidence-based pseudo-labelling idea on a separate held-out Wednesday group.

Final verified result:

| Metric | Adapted baseline | Candidate | Change |
|---|---:|---:|---:|
| Attack recall | **98.39%** | **97.65%** | **-0.74 percentage points** |

Pseudo-update contamination was **0.01%**. Under the predefined Experiment 2 limits, a candidate was harmful if benign false-positive rate increased by more than 0.1 percentage points or attack recall decreased by more than 5 percentage points. The candidate did **not** cross those limits and was therefore classified as **NOT HARMFUL under the predefined limits**.

Experiment 2 removed the 0%-recall floor and made the comparison measurable, but it did not confirm the harmful-update hypothesis.

## Main Interpretation

Experiment 1 exposed an important design limitation:

> A relative safety rule can be uninformative when the reference model already fails completely on the new attack distribution.

The project also showed that high model confidence can coexist with incorrect pseudo-labels under changed traffic. However, contamination alone does not prove that an update causes measurable performance harm.

The repository does **not** claim that outdated audits generally approve harmful updates, and it does **not** claim a novel detection method.

## Open Questions

The following are **untested hypotheses or unresolved questions**, not findings:

1. **When does contamination become measurable harm?** Experiment 1 had severe pseudo-label contamination but a 0%-recall floor prevented a meaningful harmful-update comparison. Experiment 2 removed the floor but did not cross the predefined harm thresholds.
2. **Why did Experiment 2's selected pseudo-update set have far lower contamination?** Possible explanations include the verified adaptation seed changing score separation, changes in which flows passed the 0.99 benign-confidence threshold, or class-composition differences. These explanations have not been tested.
3. **How should update safety be assessed when the baseline itself is weak on a changed distribution?** A future design could compare absolute and relative safety criteria while preserving untouched evaluation data.
4. **How stable are confidence scores under distribution change?** Post-hoc calibration or score-distribution diagnostics could be informative, but any such analysis should be labelled exploratory and should use only already-seen data unless a new untouched dataset is introduced.

## Limitations

- CIC-IDS2017 day blocks confound capture day with attack-family changes.
- The CSV files do not provide a reliable row-level timeline for a real streaming experiment.
- Wednesday groups are held-out samples from one capture day, not successive verified deployment windows.
- The Experiment 1 baseline had 0% recall on the new Wednesday attacks, creating a floor effect.
- The 200-record recent-audit script is exploratory and too small for strong statements about very low false-positive rates.
- CIC-IDS2017 contains duplicate-feature and conflicting-label artefacts that require careful handling.
- The current experiments do not test explainability or human interaction with AI systems.

## Research Integrity

The Wednesday blind evaluation was consumed during Experiment 1. It must not be reused as a fresh blind test after redesigning the hypothesis or update method.

Experiment 2 is therefore explicitly labelled exploratory rather than presented as a new blind confirmation.

Any future confirmatory experiment should use previously untouched data or a newly pre-specified split, define metrics and thresholds in advance, and avoid a baseline condition where deterioration is impossible to measure.

## Reproducibility

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for:

- environment setup;
- official CIC-IDS2017 source;
- expected data layout;
- fixed random seeds;
- Experiment 1 run order;
- Experiment 2 run order;
- generated artefacts and excluded data.

`requirements.txt` records the Python package versions used in the current environment.

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
│   ├── experiment2_protocol.md
│   ├── create_splits.py
│   ├── train_baseline.py
│   ├── train_candidate.py
│   ├── audit_old_model.py
│   ├── audit_recent_model.py
│   ├── evaluate_blind_test.py
│   ├── check_update_contamination.py
│   ├── experiment2_create_splits.py
│   ├── experiment2_train_adapted_baseline.py
│   ├── experiment2_train_candidate.py
│   └── experiment2_evaluate.py
├── RESULTS.md
├── CODE_AUDIT_NOTES.md
├── REPRODUCIBILITY.md
├── requirements.txt
├── LICENSE
└── README.md
```

Raw data, processed data, trained-model artefacts, virtual environments and Python cache files are excluded through `.gitignore`.

## License

The repository's code is released under the MIT License. See [`LICENSE`](LICENSE). The CIC-IDS2017 dataset remains subject to the terms of its original publisher and is not redistributed here.

## Author

**James Ilemona Akor**  
Cybersecurity and machine-learning research experiment.
