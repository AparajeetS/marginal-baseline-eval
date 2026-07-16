# REF Complexity 2023 Intake

Study: Teng et al., *Finding Generalization Measures by Contrasting Signal and
Noise*, ICML 2023.

Official paper page: https://openreview.net/forum?id=PQgjker1cd

Official code: https://github.com/962086838/REF-complexity

Artifact commit inspected: `a5ccdf96af722f860a16e93da4daabe3572cc659`.

## Intake Result

The repository contains the metric implementation and aggregation code. Its
README reports more than one hundred ResNet-20/32/56 experiments on CIFAR-10
and CIFAR-100. The aggregation scripts parse architecture, batch size, learning
rate, weight decay, test accuracy, train/test loss gap, and REF variants from
per-run logs, which would satisfy the MBE run-level schema.

However, the committed `output/example_log.txt` and
`result/example_result.txt` files are empty placeholders. The run logs needed
to reproduce the published correlations are not present. Exact reproduction
and reaudit are therefore blocked by artifact availability, not compute.

No result from this study is currently counted as an MBE reproduction.
