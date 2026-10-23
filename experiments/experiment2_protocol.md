# Experiment 2: Exploratory Adapted-Baseline Follow-Up

## Purpose
Experiment 1 could not test whether pseudo-labelled self-training reduced unseen-attack recall because the original baseline already had 0% recall on Wednesday attacks.

Experiment 2 removes that floor effect by first giving the model a small, verified Wednesday feedback set. It then asks whether the same confidence-based pseudo-labelling strategy can degrade performance after the model has acquired some competence on the newer attack distribution.

## Status
This is an **exploratory follow-up**, not a new blind confirmation. Wednesday labels were already revealed during Experiment 1. The held-out set below is kept separate inside Experiment 2, but it must not be described as a never-seen project-level blind test.

## Fixed Design
1. Reuse only Wednesday rows that survived Experiment 1's float32 leakage quarantine.
2. Repartition Wednesday feature fingerprints using random seed 2026 into:
   - verified_seed_pool: 20%
   - pseudo_update: 50%
   - heldout_eval: 30%
3. Keep identical float32 feature fingerprints inside one group only.
4. Build an adapted baseline from:
   - the original Monday/Tuesday training set, plus
   - up to 2,000 verified Wednesday benign rows and 2,000 verified Wednesday attack rows from verified_seed_pool.
5. Select up to 20,000 pseudo_update rows that the adapted baseline predicts BENIGN with probability >= 0.99.
6. Retrain the same Random Forest architecture with those selected rows pseudo-labelled as benign. True pseudo_update labels are not read during candidate training.
7. Evaluate adapted baseline and candidate on heldout_eval.
8. After training is complete, reveal the selected pseudo_update labels to measure contamination.

## Predefined Comparative Harm Limits
The candidate is considered harmful relative to the adapted baseline if either:
- benign false-positive rate increases by more than 0.1 percentage points, or
- attack recall decreases by more than 5 percentage points.

These are experimental thresholds, not production safety guarantees.

## Interpretation Rule
A positive result would show that contaminated pseudo-labelling can damage an already-partly-adapted model. A negative result would mean the tested update did not cross the predefined harm limits. Either result must be reported.
