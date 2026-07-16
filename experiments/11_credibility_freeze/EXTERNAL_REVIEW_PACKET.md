# External Adversarial Review Packet

The reviewer is asked to find reasons the MBE conclusions should not be trusted.
Agreement is not the deliverable; a public discrepancy report is.

## Review Questions

1. Does the baseline ladder answer a scientifically meaningful estimand?
2. Can any target component leak into controls, metrics, folds, or selection?
3. Are configuration groups the correct independent units?
4. Is residual permutation described only as a diagnostic where clustered
   exchangeability is uncertain?
5. Does the refit bootstrap capture the material nuisance and split uncertainty?
6. Are CMI, granulated Kendall, robust sign error, and MBE described without
   collapsing their different questions?
7. Can a known proxy pass every eligible nuisance learner?
8. Is any blocked claim stated affirmatively elsewhere in the repository?
9. Does the paper distinguish learner-relative predictive utility from universal
   conditional information?

## Reviewer Deliverables

- environment and conflict disclosure;
- commit and container digest used;
- commands executed and raw logs;
- discrepancies classified as material, interpretive, or cosmetic;
- signed conclusion even when replication fails.

The project owner should not provide expected protected-task values before the
reviewer commits their report.
