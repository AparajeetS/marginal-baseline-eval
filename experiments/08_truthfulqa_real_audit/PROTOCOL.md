# Prospective Protocol: TruthfulQA Reference-Difference Pilot

**Protocol status:** amended and frozen before computing the candidate audit result

**Initial freeze:** commit `5db33e4d8afadd9e1df730c7ea006d48902af4b1`, 2026-07-16

**Reason for pre-result amendment:** source inspection found duplicated prompts, conflicting labels, and exact benchmark-reference answers in the released label pool. It also established that the label triples align with TruthfulQA v0 rather than the later v1 table. The cohort and claim were narrowed before running the score so those facts could not mechanically manufacture a positive result.
**Registration boundary:** the Git history is a time-ordered protocol freeze, not a third-party preregistration.

No candidate-score audit result was computed before this amendment. The analysis may support, fail to support, or leave the scoped claim unresolved. The result will be reported regardless of direction.

## Purpose and Scoped Claim

This pilot is a real-data test of selected E0-E2 checks in the experimental Benchmark Audit Toolkit. It does not validate MBE, certify TruthfulQA, establish construct validity, or evaluate any model as truthful.

The candidate claim is:

> Within the released TruthfulQA v0 human-labelled answer triples, after removing duplicated conflicts and exact benchmark-reference answers and grouping by question, a transparent ROUGE-1-style reference-difference score adds out-of-question predictive information for the original human binary truth judgments beyond the declared response and task proxies; the pilot separately tests whether that increment transports in aggregate across sufficiently represented question categories.

The original human judgments are external to the automated score but are not an independent benchmark: both were produced within the TruthfulQA evaluation framework.

## Frozen Source Contract

The only source is the official `sylinrl/TruthfulQA` repository at commit `d71c110897f5d31c5d7f309e7bc316c152f6f031`, licensed Apache-2.0.

- v0 question metadata and references: `data/v0/TruthfulQA.csv`
  - expected questions: 817
  - SHA-256: `f4fcc4a841d4474c46a4719c295c6df5f12eef14c187fbb9637a29e70d9ece00`
- Human truth-label triples: `data/finetune_truth.jsonl`
  - expected raw rows: 22,434
  - SHA-256: `9fd94fc943a2dc08f1dc028d2b6f353ae85fae5169a536ae6489236db2f30b64`
- Human informativeness-label triples, used only for a sensitivity analysis: `data/finetune_info.jsonl`
  - expected raw rows: 22,434
  - SHA-256: `5956ef2070055e3ae0020d510007f5b9eb841719c9e3320e38fd7e2ee340b69e`
- Official metric code, used to document the reference-difference structure but not imported: `truthfulqa/metrics.py`
  - SHA-256: `0a4667429a13b2f75704af631ac001674a60c74c8e2955c8431d5b0faddb7b12`

A failed hash, unexpected raw row count, unparseable record, or label outside `{yes, no}` stops the analysis. Cohort exclusions described below are counted and published rather than treated as errors.

## Frozen Cohort Construction

The following operations are applied in this order without consulting the candidate score:

1. Parse each prompt into its exact question and answer strings.
2. Collapse duplicate `(question, answer)` pairs. Discard the entire pair if its released truth labels conflict; otherwise retain one row.
3. Join questions exactly to the v0 table. Drop and count unmatched pairs rather than silently joining approximately.
4. For leakage detection only, normalize answers and references with Unicode NFKC, case-folding, whitespace collapse, and removal of one terminal period. Split reference lists on semicolons.
5. Exclude any answer that exactly matches a supplied correct reference, an incorrect reference, or `I have no comment.` after that normalization. The last phrase is included because the official generative metric code adds it to the correct-reference set. This prevents author-written references from mechanically validating a reference-similarity score.
6. Define the main transport cohort by retaining categories with at least 20 distinct eligible questions. This rule uses only question identity and category, not target labels or candidate scores. Publish the retained category list and an all-category sensitivity summary.

Every remaining answer for a question stays in the same E1 fold. Source rows and raw text are not committed to the derived ledger; stable question IDs and aggregate exclusion counts are retained.

## Frozen Variables

- Candidate score, `reference_overlap_diff`: add `I have no comment.` to the correct references; compute multiset unigram-token F1 between the answer and every reference; take maximum correct-reference F1 minus maximum incorrect-reference F1.
- Target, `human_truth_label`: 1 for a released `yes` judgment and 0 for `no`.
- Declared response and task proxies:
  - `answer_length_tokens`
  - `question_length_tokens`
  - `refusal_or_uncertainty_flag`
  - `question_type` (`Adversarial` or `Non-Adversarial`)
  - `correct_reference_count`
  - `incorrect_reference_count`
- Environment: author-defined TruthfulQA `Category`, restricted by the frozen coverage rule for the main E2 analysis.
- Independence unit: stable question ID.
- Deceptive control: `length_proxy_control`, answer length plus deterministic sub-token jitter. It is intentionally associated with a declared baseline but contains no answer semantics.
- Negative control: `hash_noise_control`, deterministic pseudo-random noise derived only from the question-answer text hash.

Tokenization lowercases and extracts Unicode word tokens. Unigram F1 uses multiset-token precision and recall. Empty-versus-empty receives 1; one empty input receives 0. This is a transparent reimplementation of the official max-correct-minus-max-incorrect ROUGE-1 reference-difference structure. It is not represented as the exact T5 ROUGE implementation or as an official TruthfulQA score.

`refusal_or_uncertainty_flag` is 1 if the normalized answer contains one of: `i have no comment`, `i don't know`, `i do not know`, `unknown`, `unclear`, `not known`, `no one knows`, `cannot be determined`, or `can't be determined`; otherwise it is 0.

## Frozen Estimation and Decision Rules

- Five-fold question-grouped cross-fitting for E1.
- Second-degree numeric terms, training-fold-only empirical ranks and scaling, ridge penalty `0.001`.
- Aggregate leave-one-category-out transport for E2.
- Seed `20260716`.
- 199 permutations and 499 question- or category-level bootstrap resamples, as applicable.
- A positive practical threshold of 1% relative out-of-fold MSE improvement is required separately for E1 and E2.
- An estimand meets its threshold only if its point estimate is at least 1% and the 95% bootstrap interval for absolute MSE improvement is entirely above the corresponding 1% baseline-MSE threshold.
- It falls below the threshold only if the interval is entirely below that threshold; otherwise it is unresolved.
- The overall predeclared-test outcome supports the scoped claim only if both E1 and E2 meet their thresholds and neither supplied control meets either threshold. Any control crossing a threshold makes the outcome unresolved.

E0 is descriptive only. E3 interventions and E4 reliability/cost are outside this pilot and remain explicitly unimplemented.

## Frozen Sensitivity Analyses

1. Publish descriptive counts, label prevalence, and mean candidate score for every eligible category so the aggregate E2 result cannot stand in for every category.
2. On rows with a nonconflicting exact `(question, answer)` match in `finetune_info.jsonl`, compare the declared primary baseline specification with an enriched specification that adds the released human informativeness label. This shares the annotation pipeline, is not a deployment-available capability proxy, and is not part of the primary pass/fail rule.
3. Report cohort construction for all 38 categories, while keeping the at-least-20-question cohort as the only predeclared E2 decision cohort.

## Permitted Interpretation

The strongest permitted conclusion concerns incremental prediction of the original human judgments by this transparent lexical score under the frozen exclusions, proxies, grouping, categories, and estimators. Model identity, family, size, prompt, and general capability are unavailable, so the audit does not control them or test model-family transport. The same project produced the references and judgments; annotator identities and uncertainty are unavailable; categories are author-defined and unequal; v0 contains questions later revised or removed; and lexical overlap can reward surface similarity. E2 is an environment-equal aggregate and may hide individual-category failures. These limitations accompany the result even if both declared thresholds are met.
