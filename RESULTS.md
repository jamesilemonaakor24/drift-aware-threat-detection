# Experiment 1 Results

## Question

Can a model update pass a safety check based on older traffic while becoming harmful on newer traffic?

## Outcome

**Inconclusive for the original harmful-update hypothesis.**

The experiment did not show that the candidate became measurably worse than the frozen baseline on Wednesday, because both models already had 0% recall on the Wednesday attack traffic evaluated.

## What was demonstrated

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

## Why the main hypothesis remained unresolved

The harmful-update definition compared the candidate with the frozen baseline.

On Wednesday, the baseline already had 0% attack recall. Recall cannot decrease below 0%, so this run had a floor effect on the main unseen-attack metric.

The correct conclusion is therefore:

- high-confidence pseudo-labelling was unreliable under the changed traffic;
- the candidate was not shown to be more harmful than the baseline;
- the original harmful-update hypothesis was not confirmed.

## Follow-up Principle

Do not retune Experiment 1 against the already-consumed Wednesday blind test.

A follow-up should use untouched data or a new pre-specified split and should ensure that the chosen baseline has measurable non-zero performance on the target traffic so that deterioration can actually be observed.
