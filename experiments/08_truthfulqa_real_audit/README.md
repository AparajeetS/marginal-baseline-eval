# TruthfulQA v0 Reference-Difference Pilot

This directory contains the protocol, implementation, derived data, and claim
card for a leakage-screened real-data pilot of the experimental Benchmark Audit
Toolkit.

## Reproduce

Use Python 3.9 or newer. From the repository root:

```bash
python -m pip install -e .
git clone https://github.com/sylinrl/TruthfulQA.git ../TruthfulQA-source
git -C ../TruthfulQA-source checkout d71c110897f5d31c5d7f309e7bc316c152f6f031
python experiments/08_truthfulqa_real_audit/run_truthfulqa_audit.py --truthfulqa-root ../TruthfulQA-source
```

The runner refuses to proceed unless the TruthfulQA checkout and four source
file hashes match the frozen contract. It regenerates the derived ledger,
category summary, cohort manifest, primary claim card, result summary, and
human-informativeness sensitivity bundle in `artifacts/`.

## Audit Boundary

The candidate is a transparent unigram-F1 reference-difference score, not the
exact official T5 ROUGE implementation. The target is the original released
human truth judgment. Model identities and general capability are unavailable.
Accordingly, the pilot tests a narrow out-of-question and aggregate
category-transport prediction claim. It does not validate MBE, TruthfulQA, or a
truthfulness construct, and it does not certify any benchmark or model.

The initial protocol freeze is commit
`5db33e4d8afadd9e1df730c7ea006d48902af4b1`. The governing leakage amendment was
frozen before analysis at commit
`827e192729b1b26dd8c470ae70f028214c942090`.
