
# Experiment 1: Can Old Safety Tests Approve Harmful Model Updates?

## Research Question
Can an intrusion detection model pass a safety check using old data but perform worse on newer network traffic?

## Hypothesis
An old validation dataset may approve harmful model updates that a small, independently verified recent sample could detect.

## Dataset
CIC-IDS2017 (MachineLearningCVE CSV files).

## Experiment
- Train an original threat detection model.
- Create updated versions using newer traffic.
- Test each update using historical validation data.
- Test the same updates using separate, verified newer data.
- Evaluate the updates on untouched data to determine whether they were harmful.

## Important Limitation
Our CSV files identify capture days but do not contain individual flow timestamps. This is a cross-session experiment, not a real-time deployment test.

## Research Rule
We will report both positive and negative results. We will not assume the hypothesis is correct.

## Initial Experimental Setup

Training period: Monday and Tuesday.

First unseen attack family: DoS Hulk (Wednesday).

Wednesday data will be divided into separate groups for:
- Creating model updates
- Checking updates using verified recent data
- Independently testing the updates

Identical network-flow features must not appear
across training, validation, and testing groups.

We will check duplicates before dividing the data.

Important: Wednesday groups are from the same
capture day, so this is not a real-time experiment.



## Duplicate and Conflicting Feature Audit

The initial audit identified:

- 8,271 feature fingerprints shared across capture days.
- 74 fingerprints with conflicting binary labels.
- 4,486 records belonging to conflicting groups.
- Most affected attack records belong to DoS Hulk.

Experimental decisions:

1. Keep the original and processed datasets unchanged.
2. Quarantine conflicting fingerprint groups for the primary experiment.
3. Prevent identical feature fingerprints from appearing
   in different training, validation, or evaluation groups.
4. Run a later sensitivity test including conflicting groups
   to measure whether their exclusion affects the results.

Matching features do not necessarily mean two records
represent the same real network event.


## Baseline Model Results

Model: Random Forest
Training data: Monday and Tuesday

### Original Model
- Known attacks detected: 1,217/1,217
- Missed attacks: 0
- False alarms: 1
- Attack recall: 100%

### Destination Port Ablation
A second model was trained without Destination Port.

- Known attacks detected: 1,211/1,217
- Missed attacks: 6
- False alarms: 1
- Attack recall: 99.51%

### Observation
Removing Destination Port caused a small reduction
in detection performance.

This suggests that the model also relies on
other network features.

These results only concern familiar attack types
from the Monday/Tuesday capture sessions.

Wednesday's blind evaluation remains unused.

### Decision
Keep the original Random Forest as the initial
baseline. Do not change its features based on
Wednesday's blind evaluation.


## Defining a Harmful Model Update

We compare every updated model with the
original frozen Random Forest.

A model update may be considered harmful if:

1. It produces too many additional false alarms
   on normal network traffic.

2. It loses too much ability to detect known attacks.

3. It performs significantly worse than the
   original model on previously unseen attacks.

The acceptable limits will be selected and recorded
before evaluating candidate updates.

## False-Safe Approval

A false-safe approval happens when:

- A safety audit approves an updated model.
- An independent blind evaluation later shows
  that the update was harmful.

Our main experiment measures how frequently
this happens.

We will compare historical-only audits with
audits using a small amount of verified recent data.

Both approaches must assess identical candidate
models under fair, documented conditions.

We will also record useful updates that the
safety checks incorrectly reject.


## Predefined Safety Limits

All candidate updates will be compared with the
original frozen Random Forest.

For this initial experiment, an update is harmful if
any of the following occurs on independent evaluation:

1. Benign false-positive rate increases by more
   than 0.1 percentage points.

2. Known-attack recall decreases by more
   than 5 percentage points.

3. Unseen-attack recall decreases by more
   than 5 percentage points.

The same limits will be used by both safety-audit
methods wherever the required classes are represented.

A class missing from an audit cannot be treated
as successfully checked.

These are predefined experimental thresholds,
not guarantees of real-world security.

We will record all approval, rejection, and
inconclusive decisions.

We will not change these limits after viewing
the blind evaluation results.


## Experiment 1 Outcome

The original harmful-update hypothesis was **not demonstrated** in this run.

Observed results:

- The historical Monday/Tuesday audit approved the candidate because its false-positive rate and known-attack recall did not worsen relative to the frozen baseline.
- The 20,000 Wednesday flows pseudo-labelled as benign were later found to contain 7,222 attacks, a contamination rate of 36.11%.
- The baseline and candidate both had 0% recall on the Wednesday attack traffic evaluated.
- Because the baseline was already at a 0% recall floor, the candidate could not show a further decrease in unseen-attack recall.

Interpretation:

1. High confidence from the baseline was not a reliable guarantee of correct pseudo-labelling under the Wednesday distribution.
2. The experiment did not establish that the candidate update became more harmful than the baseline.
3. The relative safety thresholds were insufficient to resolve the main hypothesis once the baseline itself failed completely on the new attacks.
4. Experiment 1 is therefore reported as **inconclusive for harmful-update approval**, while the update-contamination finding is retained as a valid observation.

Research-integrity rule:

The Wednesday blind test has now been consumed. Any redesigned follow-up must use previously untouched data or a new pre-specified split. The thresholds or hypothesis must not be retroactively changed and then re-tested on the same blind set as though it were still unseen.
