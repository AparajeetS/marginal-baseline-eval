# VM 999-Refit Sensitivity

The B1, B2, and B3 chunks completed independently on the 16-vCPU VM with 999
full refit-bootstrap draws per metric and nuisance family.

Across all 42 baseline-by-metric comparisons, including the random negative
control, zero metrics had positive refit lower bounds under both nuisance
families. This agrees with the earlier 199-refit strict consensus decisions.

The observed-design power calibration subsequently showed that this strict
two-family rule has almost no power at 36 configurations because the
interaction nuisance family vetoes signals recovered by the additive family.
The 999-refit result therefore establishes that the abstention is stable to
Monte Carlo error; it does **not** establish that the metrics contain no
incremental information.

Artifacts:

- [`out_vm_refit999_b1/`](out_vm_refit999_b1/)
- [`out_vm_refit999_b2/`](out_vm_refit999_b2/)
- [`out_vm_refit999_b3/`](out_vm_refit999_b3/)
- [observed-design power results](../16_causal_text_observed_design_power/PRIMARY_RESULTS.md)

