# MBE Benchmark Claim Card

> Experimental research prototype. Not independently validated. This card is a scoped diagnostic, not certification.

**Predeclared test outcome:** `supports-claim-under-declared-tests`

**Interpretation:** The candidate crossed the predeclared E1 and aggregate E2 thresholds in these data while the supplied controls did not. This is conditional evidence, not certification or construct validity.

## Scoped Claim

- ID: `truthfulqa-v0-reference-difference-pilot-v1`
- Text: Within the released TruthfulQA v0 human-labelled answer triples, after removing duplicated conflicts and exact benchmark-reference answers and grouping by question, a transparent ROUGE-1-style reference-difference score adds out-of-question predictive information for the original human binary truth judgments beyond the declared response and task proxies; the pilot separately tests whether that increment transports in aggregate across sufficiently represented question categories.
- Candidate score: `reference_overlap_diff`
- Named outcome: `human_truth_label`
- Declared baselines or proxies: `answer_length_tokens`, `question_length_tokens`, `refusal_or_uncertainty_flag`, `question_type`, `correct_reference_count`, `incorrect_reference_count`
- Environment: `category`
- Independence unit: `question_id`

## Estimand Results

| ID | Check | Predeclared test outcome | Main quantity |
|---|---|---|---:|
| E0 | Unconditional association | unresolved | rho +0.3389 |
| E1 | Increment beyond declared baselines | meets-declared-threshold | relative MSE +0.1233 |
| E2 | Aggregate environment holdout | meets-declared-threshold | relative MSE +0.1101 |
| E3 | Matched interventions | unresolved | n/a |
| E4 | Reliability and cost | unresolved | n/a |

## Declared Control Results

| Score | Kind | E1 | E2 |
|---|---|---|---|
| `length_proxy_control` | deceptive | below-declared-threshold | below-declared-threshold |
| `hash_noise_control` | negative | below-declared-threshold | below-declared-threshold |

## Limitations

- The labels and answer pool are released TruthfulQA v0 data, not a fresh confirmatory holdout.
- The same project produced the human judgments and reference framework, so the target is external to the automated score but not an independently constructed benchmark.
- Model identity, family, size, prompt, and general capability are unavailable; this pilot neither controls them nor tests model-family transport.
- The transparent lexical score follows the official reference-difference structure but is not the exact T5 ROUGE implementation or an official score.
- Exact reference answers, duplicate conflicts, poorly represented categories, and unmatched questions were excluded by the frozen rules; the result applies only to the resulting cohort.
- Categories are author-defined and unequal; aggregate E2 can hide individual-category failures, so category summaries are published separately.
- Reference overlap can reward surface similarity and does not by itself establish truthfulness or construct validity.
- Results are conditional on the named outcome, data, split, estimator, declared baselines, environments, and analysis settings.
- Declared baselines and proxies do not exhaust latent capability, response style, task structure, or all possible confounding.
- Empirical rank transforms and numeric scaling are fitted within each training fold; results remain conditional on the chosen folds and finite-sample transformations.
- The E2 result is an environment-equal aggregate and can hide a failing individual environment.
- E3 interventions and E4 measurement reliability/cost are not implemented.
- Association and incremental prediction do not establish causality or construct validity and do not certify a benchmark or model.

## Synthetic-Control Boundary

Synthetic controls test implementation behavior under their chosen data-generating assumptions. Passing them does not validate MBE or its real-world benchmark use.
