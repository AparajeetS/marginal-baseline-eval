# Tiny MBE Audit

- Target: `test_accuracy`
- Controls: `learning_rate`, `weight_decay`, `arch`
- Example ledger: `examples/tiny_metric_ledger.csv`

| Metric | n | Raw rho | MBE partial rho | Delta | Class |
|---|---:|---:|---:|---:|---|
| `fim_norm` | 6 | +1.000 | +1.000 | +0.000 | survives |
| `val_loss_ep20` | 12 | -1.000 | -1.000 | +0.000 | survives |
| `val_loss_ep20` | 6 | -1.000 | -1.000 | +0.000 | survives |
| `fim_norm` | 6 | +0.943 | +0.433 | -0.510 | survives |
| `val_loss_ep20` | 6 | -1.000 | -0.406 | +0.594 | survives |
| `fim_norm` | 12 | +0.888 | +0.162 | -0.727 | weak-or-mixed |

Class counts: survives: 5, weak-or-mixed: 1.
