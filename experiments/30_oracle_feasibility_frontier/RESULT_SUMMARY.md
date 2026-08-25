# Oracle Feasibility Frontier Results

Status: complete and independently validated locally. This is a known-truth
diagnostic; it does not authorize opening any protected empirical association.

## Completion

- 126,000 / 126,000 planned dataset rows
- 336 dataset cells and 1,344 method-summary rows
- zero non-estimable rows
- zero duplicate task keys
- exact repetition balance: 500 at 24/48 configurations and 250 at 96/192
- all frozen source hashes matched remotely and locally
- manifests report no protected target or checkpoint-metric reads

## Main Result

The experiment separates information, measurement, and nuisance-estimation
limits for the frozen conditional-covariance estimand.

At **24 independent configurations**, the latent-signal ceiling passed both
gates, but the observable oracle did not reach useful effect-0.50 power. Its
weakest power was 36.4% (Wilson lower bound 32.3%), despite calibrated null
behavior. This is evidence that the observed metric/noise regime is
information-limited at 24 configurations, even when the nuisance functions are
known exactly.

At **48 configurations**, the observable oracle passed both frozen gates:
worst null support was 4.0% (Wilson upper bound 6.1%) and weakest effect-0.50
power was 72.0% (Wilson lower bound 67.9%). Both learned degree-2 estimators had
useful power but failed calibration. Learned raw residualization reached 14.2%
worst null support; learned rank residualization reached 15.2%. This identifies
nuisance estimation, rather than absence of usable information, as the binding
problem in the 48-configuration regime.

At **96 and 192 configurations**, learned false support decreased but remained
above the frozen calibration gate. The learned raw worst-null rates were 10.8%
and 9.2%; the learned rank rates were 10.4% and 8.0%. Power was high. Exact
oracle empirical null rates remained close to nominal at 4.8%, but their Wilson
upper bounds were 8.2%, so they did not pass the unusually strict 7.5% frozen
upper-bound gate with only 250 repetitions. This is a binding preregistered
failure, not evidence that the exact oracle became less calibrated as sample
size increased.

## Interpretation

The result supports a sample-size-aware research direction:

- 24 configurations are too weak in the studied noisy observable regime;
- 48 configurations contain enough information in principle;
- the current learned nuisance procedures create excess false support;
- merely increasing to 96 or 192 configurations improves but does not repair
  their worst-cell calibration;
- measurement reliability and nuisance estimation must be treated as separate
  audit bottlenecks.

This is positive evidence for the need for an MBE-style calibration layer, but
not validation of the current learned MBE rule. The protected image, text, and
PGDL associations remain sealed. The next estimator should target the observed
48-configuration oracle gap and must be confirmed on fresh known-truth data
before any real-data opening decision.

## Claim Boundary

The latent ceiling is an optimistic diagnostic, not a deployable method. The
observable oracle is design-specific and not a universal upper bound. The
Student inference used in this frontier is a computational diagnostic and does
not replace previously frozen wild-bootstrap procedures. These simulations do
not establish arbitrary conditional independence, causal importance, universal
metric rankings, or production readiness.

