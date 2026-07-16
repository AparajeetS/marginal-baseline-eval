# MBE Protocol Calibration

These synthetic cases have known data-generating structure. Passing means the declared audit profile matched that structure under the frozen thresholds; it does not validate MBE on real model populations.

| Scenario | Expected profile | Raw rho | Partial rho | Cross-fit residual rho | Delta MSE | Pass |
|---|---|---:|---:|---:|---:|---|
| null_metric | no-increment | -0.026 | -0.029 | -0.098 | -0.0000 | yes |
| linear_proxy | proxy-washout | 0.889 | -0.013 | 0.020 | -0.0003 | yes |
| nonlinear_proxy | nonlinear-proxy-washout | 0.942 | 0.942 | -0.124 | 0.0000 | yes |
| genuine_increment | increment-survives | 0.724 | 0.874 | 0.819 | 0.0418 | yes |
| heteroskedastic_null | conditional-null | -0.103 | -0.034 | -0.050 | -0.0001 | yes |
| clustered_null | conditional-null | 0.795 | 0.007 | 0.029 | -0.0011 | yes |
| simpson_increment | increment-after-environment-control | -0.427 | 0.804 | 0.817 | 0.0161 | yes |
| post_treatment_control | estimand-warning | 0.900 | 0.018 | 0.085 | -0.0004 | yes |

The nonlinear-proxy case is intentionally diagnostic: linear partial ranks retain a false signal, while the cross-fitted polynomial nuisance model should remove it. The post-treatment case is an estimand warning, not evidence that the original metric has no total effect.
