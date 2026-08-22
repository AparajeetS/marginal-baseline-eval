# Corrected Image Factorial

This experiment is the corrected prospective image counterpart to the causal
text factorial. It trains a balanced 96-run CIFAR-10 grid and records repeated
diagnostic batches, protected test outcomes, complete configuration identity,
and a valid run-level random control.

The experiment is separate from the legacy 680-row pool and earlier
time-boxed image holdout. See `PREREGISTRATION.md` for the frozen claim and
completion boundaries.

## Kaggle

Kernel: `aparajeetshadangi/mbe-3-corrected-image-factorial`

Expected outputs:

- `mbe3_corrected_image_factorial.csv`
- `mbe3_corrected_image_factorial_manifest.json`
- `mbe3_corrected_image_factorial_integrity.json`

Run a local structural smoke test with:

```powershell
python mbe3_corrected_image_factorial.py --smoke --epochs 1 --n-train 128 --n-val 64 --n-test 64 --metric-n 4 --max-hours 0.2
```
