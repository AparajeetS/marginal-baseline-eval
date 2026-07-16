# Prospective Metric Selection Protocol

Status: frozen design for testing operational value after the atlas is built.

## Question

Can a recommendation produced without seeing a future task outcome reduce the
regret of choosing a metric for that declared target and measurement budget?

## Freeze Boundary

Before generating prospective outcomes, publish:

- eligible metric cards and implementations;
- target, baseline level, and utility function;
- selector features available at recommendation time;
- nuisance learners, outer task-family splits, and tuning grid;
- abstention threshold and practical-significance threshold;
- comparator implementations;
- run IDs, dataset splits, and analysis command.

No component may change after prospective target values are inspected. A dated
amendment requires a new untouched outcome batch.

## Evaluation Unit

The independent unit is a task family. Models or seeds within one family do not
increase the transport sample size. With fewer than 12 families the result is a
feasibility study; 20 or more are preferred for a primary selector claim.

## Frozen Comparators

1. globally best metric on development families;
2. pooled raw-correlation selector;
3. within-task correlation when historical target-task outcomes are allowed;
4. baseline-only prediction;
5. regularized stacking of all eligible metrics;
6. random eligible metric;
7. task-specific oracle as an unattainable upper bound;
8. MBE selector without abstention;
9. MBE selector with abstention.

## Outcomes

- normalized selection regret;
- top-1 and top-3 utility recovery;
- sign-error rate;
- interval coverage;
- coverage-regret and coverage-risk curves;
- metric-computation cost at matched regret;
- abstention reasons and task-family count.

## Success Gate

The selector becomes a paper contribution only if it improves held-out-family
regret over both the globally best metric and pooled-correlation selector, and
abstention reduces regret monotonically over a useful coverage range. Otherwise
the selector claim is withdrawn and the reliability atlas remains the output.
