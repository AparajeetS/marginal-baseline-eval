# Run-Level Artifact Request

Subject: Request for REF Complexity run-level logs for independent metric audit

Hello,

I am reproducing published generalization-measure evaluations as part of the
open Marginal Baseline Evaluation project. I inspected the official REF
Complexity repository at commit
`a5ccdf96af722f860a16e93da4daabe3572cc659`. The aggregation code appears to
contain everything needed, but the committed example result and log files are
empty.

Would you be willing to share the per-run logs or the aggregated run-level table
used for the CIFAR-10 and CIFAR-100 results? The minimum useful columns are:

- run ID and dataset;
- architecture/depth and random seed;
- batch size, learning rate, weight decay, augmentation, and training budget;
- train loss, test loss or generalization gap, and test accuracy;
- REF Complexity and any reported ablation variants;
- exclusion or failed-run status.

The goal is first to reproduce the published correlation, then apply several
conditional and environment-aware evaluations. The reproduction, discrepancies,
and any negative result will be reported publicly with attribution to the
official artifact. Raw data need not be redistributed if licensing prevents it;
a checksum and download script or derived table would be sufficient.

Thank you,

Aparajeet Shadangi
https://github.com/AparajeetS/marginal-baseline-eval
