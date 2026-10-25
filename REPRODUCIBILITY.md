# Reproducibility Guide

This repository contains the code and protocols used for two exploratory experiments on model-update safety with the CIC-IDS2017 MachineLearningCVE / MachineLearningCSV data.

The repository does **not** include raw or processed CIC-IDS2017 data, trained models, or experiment artefacts.

## 1. Environment

Create and activate a Python virtual environment, then install the pinned dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Dataset

Use the CIC-IDS2017 dataset published by the Canadian Institute for Cybersecurity, University of New Brunswick:

https://www.unb.ca/cic/datasets/ids-2017.html

This project uses the MachineLearningCVE / MachineLearningCSV files.

Place the downloaded raw CSV files under:

```text
data/raw/MachineLearningCVE/
```

Do not commit the dataset to the repository.

## 3. Preprocess and verify the data

Run:

```bash
python src/preprocess_data.py
python src/verify_processed_data.py
```

Processed files are written to:

```text
data/processed/
```

## 4. Experiment 1 fixed randomness

Experiment 1 uses seed **42** for:

- fingerprint-group shuffling in `experiments/create_splits.py`;
- the Random Forest baseline's `random_state` in `experiments/train_baseline.py`;
- the random sample of up to 20,000 high-confidence pseudo-benign update flows in `experiments/train_candidate.py`.

The Experiment 1 protocol is documented in:

```text
experiments/experiment_protocol.md
```

## 5. Experiment 1 run order

A practical reproduction order is:

```bash
python experiments/check_duplicates.py
python experiments/create_splits.py
python experiments/check_float32_leakage.py
python experiments/check_experiment_data.py
python experiments/check_split_labels.py
python experiments/train_baseline.py
python experiments/test_baseline.py
python experiments/train_candidate.py
python experiments/audit_old_model.py
python experiments/audit_recent_model.py
python experiments/check_update_contamination.py
python experiments/evaluate_blind_test.py
```

`experiments/artifacts/` is generated locally and excluded from version control.

Important interpretation rule: the Wednesday blind evaluation was consumed during Experiment 1. It must not be treated as fresh blind evidence after redesigning the hypothesis.

## 6. Experiment 2 fixed randomness

Experiment 2 is explicitly exploratory because Wednesday labels had already been revealed in Experiment 1.

The protocol fixes seed **2026** for:

- repartitioning surviving Wednesday fingerprints into `verified_seed_pool`, `pseudo_update`, and `heldout_eval`;
- selecting the verified adaptation seed used by the adapted baseline;
- other random selections defined in the Experiment 2 scripts.

See:

```text
experiments/experiment2_protocol.md
```

## 7. Experiment 2 run order

Experiment 2 depends on the processed data, Experiment 1 split file, and original baseline model already created above.

Run:

```bash
python experiments/experiment2_create_splits.py
python experiments/experiment2_train_adapted_baseline.py
python experiments/experiment2_train_candidate.py
python experiments/experiment2_evaluate.py
```

Experiment 2's held-out evaluation is separate within the exploratory follow-up, but it is **not** described as a new project-level blind test.

## 8. Expected headline results

Experiment 1:

- pseudo-benign sample: 20,000 flows;
- actually attacks: 7,222;
- contamination: 36.11%;
- baseline and candidate Wednesday attack recall: 0%;
- harmful-update hypothesis: inconclusive because of the floor effect.

Experiment 2:

- adapted baseline attack recall: 98.39%;
- candidate attack recall: 97.65%;
- change: -0.74 percentage points;
- pseudo-update contamination: 0.01%;
- predefined harmful-update threshold was not crossed.

See `RESULTS.md` for the full reported outcomes and limitations.

## 9. Data and artefacts excluded from Git

The repository's `.gitignore` excludes:

- `.venv/`;
- Python cache files;
- `data/raw/`;
- `data/processed/`;
- `experiments/artifacts/`.

No credentials or dataset copies are required to be stored in the repository.

## 10. Scope

These experiments use network-traffic data only and involve **no human participants**.

They are cross-session machine-learning experiments rather than real-time deployment studies. Experiment 2 is an exploratory follow-up and should not be presented as independent blind confirmation of Experiment 1.
