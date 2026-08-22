# CPU Credibility Campaign

The [preregistration](PREREGISTRATION.md) defines the fixed follow-on campaign
for the 16-vCPU VM. Outputs are written to one directory per independent shard
and are merged only after every shard's exit status and hashes are recorded.

Execution begins automatically after
`experiments/16_causal_text_observed_design_power/out_primary` completes.
Runtime logs, environment details, and pooled tables are copied back into this
directory before interpretation.

The campaign is deliberately CPU-only. It strengthens inference calibration
and reproducibility; it does not replace the remaining image and language-model
GPU experiments.

Completed pooled results and their scoped interpretation are in
[`CAMPAIGN_RESULTS.md`](CAMPAIGN_RESULTS.md). Rebuild pooled tables with:

```bash
python experiments/17_cpu_credibility_campaign/merge_campaign.py
```

Rebuild the degrees 1-6 calibration table with:

```bash
python experiments/17_cpu_credibility_campaign/build_complexity_ablation.py
```
