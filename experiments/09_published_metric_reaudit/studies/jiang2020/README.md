# Jiang et al. (2020) Artifact Availability

## Study

*Fantastic Generalization Measures and Where to Find Them* introduced a
large-scale evaluation of more than 40 generalization measures over more than
10,000 trained convolutional networks.

- Paper: <https://arxiv.org/abs/1912.02178>
- OpenReview: <https://openreview.net/forum?id=SJgIPJBFvH>
- Author publication page: <https://yidingjiang.github.io/publications.html>

## Intake Result

As of 2026-07-15, the paper and author publication page expose the paper but no
run-level model ledger, checkpoint corpus, metric table, or official code link
for this study. GitHub searches using the title and distinctive metric names
also did not locate an author artifact. The aggregate tables in the paper are
rounded and do not contain one row per model.

Consequently, the study cannot currently enter the MBE benchmark under the
frozen acceptance criteria. Reconstructing pseudo-runs from its published
tables would be statistically invalid. This is an artifact-availability result,
not evidence against the study or its metrics.

## Resolution

The closest official, publicly auditable successor is the Predicting
Generalization in Deep Learning competition corpus. It was released by an
overlapping author team with checkpoints, initial weights, training data,
hyperparameters, and train/test statistics. That corpus is being ingested under
`../pgdl2020/` as the external benchmark; it is not represented as the missing
Jiang et al. dataset.
