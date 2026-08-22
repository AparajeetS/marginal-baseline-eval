# Submission Log: 2026-08-11

- Requested Kaggle ref: `aparajeetshadangi/mbe-3-multicorpus-text-atlas`
- Kaggle-normalized ref: `aparajeetshadangi/mbe-3-multi-corpus-text-atlas`
- Submitted version: 1
- Initial status: `RUNNING`
- Script SHA-256: `159999847233146a98e9220db1c78ee2d0d24a36eba0e0dafa86d858a83ba12e`
- Preregistration SHA-256: `8dad324af07bc9a1c99e6d5b890ce16a7574abce59f46dae286d4b678184d897`

Kaggle normalized the title to a different slug and emitted a metadata
warning. The running version was not restarted because its scientific code
and preregistration are unchanged; local metadata will be reconciled only
after this version finishes.

The private kernel was submitted after all three synthetic smoke environments
completed, the causal-mask test and unmasked negative control passed, and no
error or duplicate row was produced.

## Version 1 Infrastructure Failure

Version 1 stopped before corpus download or training because Kaggle assigned a
Tesla P100 (`sm_60`) while its default PyTorch wheel supported only `sm_70`
and newer. No scientific output row was produced. Version 2 restores the
previously proven PyTorch 2.4.1 CUDA 11.8 compatibility bootstrap and reconciles
the Kaggle-normalized slug. The grid, seeds, outcomes, controls, and
preregistration are unchanged. Version-2 script SHA-256:
`03c791e6f65b48445f7f8080fcce97808ab1add443632d1376c15ff34954cacd`.

## Version 2 Completion

Version 2 completed in 1.264 P100-hours. All 144 planned rows were valid, the
causal-mask controls passed, and the preregistered structural completion gate
passed. Outputs were downloaded to `kaggle_downloads/v1` and independently
validated without inspecting target-metric associations.
