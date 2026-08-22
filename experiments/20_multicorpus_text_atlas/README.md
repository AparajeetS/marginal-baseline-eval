# Multi-Corpus Causal-LM Atlas

This prospective atlas trains the same balanced causal-Transformer grid on
WikiText-2, Penn Treebank, and Tiny Shakespeare. It is designed to distinguish
within-environment metric behavior from cross-corpus transport rather than
pooling heterogeneous tasks into one ranking.

See `PREREGISTRATION.md` for the frozen grid, completion gate, and claim
boundary.

## Kaggle

Kernel: `aparajeetshadangi/mbe-3-multi-corpus-text-atlas`

Expected outputs:

- `mbe3_multicorpus_text_atlas.csv`
- `mbe3_multicorpus_text_atlas_manifest.json`
- `mbe3_multicorpus_text_atlas_integrity.json`
- `causal_mask_leakage_test.json`

Run a local structural smoke test with:

```powershell
python mbe3_multicorpus_text_atlas.py --smoke --steps 3 --batch-size 4 --sequence-length 16 --max-hours 0.2
```
