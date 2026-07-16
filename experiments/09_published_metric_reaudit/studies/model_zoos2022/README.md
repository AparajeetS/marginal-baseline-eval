# Model Zoos 2022 Corpus Intake

Study: Schuerholt et al., *Model Zoos: A Dataset of Diverse Populations of
Neural Network Models*, NeurIPS 2022 Datasets and Benchmarks.

Primary source: https://proceedings.neurips.cc/paper_files/paper/2022/hash/f94d5edb5c01715d879693ddbfdc1b98-Abstract-Datasets_and_Benchmarks.html

The corpus reports 50,360 trained models across eight image datasets and 27
zoos, with systematic hyperparameter variation, checkpoints, training metadata,
and model definitions. It is a strong candidate independent corpus for the MBE
reliability atlas because it offers many task families without new GPU training.

This is not an exact published metric-score reproduction: the source paper is a
dataset contribution rather than a generalization-measure leaderboard. Intake
requires selecting licensed zoo subsets, hashing downloads, reconstructing
train/test targets, and freezing a metric-extraction manifest before outcomes
are inspected. Large checkpoint downloads are deferred until storage and metric
scope are approved.
