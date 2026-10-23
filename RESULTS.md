# Experiment Results

## Experiment 1

### Question

Can a model update pass a safety check based on older traffic while becoming harmful on newer traffic?

### Outcome

**Inconclusive for the original harmful-update hypothesis.**

The experiment did not show that the candidate became measurably worse than the frozen baseline on Wednesday, because both models already had 0% recall on the Wednesday attack traffic evaluated.

### What was demonstrated

The pseudo-labelled update set was heavily contaminated.

| Update-set result | Count |
|---|---:|
| Selected as >=99% confident benign | 20,000 |
| Actually benign | 12,778 |
| Actually attacks | 7,222 |
| Contamination rate | **36.11%** |

Most incorrectly pseudo-labelled attacks were DoS Hulk (6,733).

The historical Monday/Tuesday audit approved the candidate because both models performed identically there:

| Metric | Baseline | Candidate |
|---|---:|---:|
| False positives | 0 | 0 |
| Missed attacks | 2 | 2 |
| Attacks detected | 3,214 | 3,214 |
| Attack recall | 99.94% | 99.94% |

### Why the main hypothesis remained unresolved

The harmful-update definition compared the candidate with the frozen baseline.

On Wednesday, the baseline already had 0% attack recall. Recall cannot decrease below 0%, so this run had a floor effect on the main unseen-attack metric.

The correct conclusion is therefore:

- high-confidence pseudo-labelling was unreliable under the changed traffic;
- the candidate was not shown to be more harmful than the baseline;
- the original harmful-update hypothesis was not confirmed.

### Follow-up principle

Do not retune Experiment 1 against the already-consumed Wednesday blind test.

A follow-up should use untouched data or a new pre-specified split and should ensure that the chosen baseline has measurable non-zero performance on the target traffic so that deterioration can actually be observed.

## Experiment 2: Exploratory adapted-baseline follow-up

### Purpose

Experiment 2 addressed Experiment 1's 0%-recall floor by first adapting the baseline with a small verified Wednesday seed. It then tested the same confidence-based pseudo-labelling idea on separate Wednesday groups.

Because Wednesday labels had already been revealed during Experiment 1, this follow-up is **exploratory** and is not presented as a new project-level blind confirmation.

### Predefined harm limits

The candidate was defined as harmful relative to the adapted baseline if either:

- benign false-positive rate increased by more than 0.1 percentage points; or
- attack recall decreased by more than 5 percentage points.

These are experimental thresholds, not production safety guarantees.

### Verified outcome

| Metric | Adapted baseline | Candidate | Change |
|---|---:|---:|---:|
| Attack recall | **98.39%** | **97.65%** | **-0.74 percentage points** |

The pseudo-update contamination rate was **0.01%**.

The candidate therefore did **not** cross the predefined harm limits and was classified as **NOT HARMFUL under the predefined limits**.

### Interpretation

Experiment 2 removed the floor effect that made Experiment 1's comparative recall test uninformative. In this adapted setting, the pseudo-updated candidate showed a small recall decrease, but the decrease was far below the pre-specified 5-percentage-point harm threshold.

The result does not confirm the harmful-update hypothesis. It shows that the redesigned comparison was measurable and that, in this particular run, the tested pseudo-update did not produce a harmful degradation under the predefined criteria.

Taken together, the experiments show why update-safety claims need both a meaningful reference baseline and explicit pre-specified comparison thresholds. They also show that pseudo-label contamination can vary substantially with the model and data setting: 36.11% in Experiment 1 versus 0.01% in Experiment 2.