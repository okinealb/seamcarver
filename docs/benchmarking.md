# Benchmarking

The benchmark suite measures vertical seam removal through
`SeamCarver.remove()`. Image construction, file decoding, and file output are
outside the timed section.

Each case uses an RGB `uint8` array generated with NumPy seed `42` and the
default `GradientEnergy` method. The suite covers square images with widths of
512, 1024, and 2048 pixels. A one-seam case records the fixed-cost baseline;
the remaining cases remove 5, 50, and 500 seams, forming a 10x progression.
A fresh `SeamCarver` is created before every round because removal mutates the
carver. Each case runs one warmup round followed by five measured rounds.

Results are grouped by seam count so each table compares the three image sizes
at the same removal count. Removing 500 seams from the 512-pixel image leaves
12 columns, making that case a near-exhaustion stress workload rather than a
linear scaling comparison.

The current suite measures vertical removal only. Horizontal removal and mixed
vertical-horizontal resizing remain separate future benchmark additions.

Install the development environment, then run the benchmarks explicitly:

```bash
uv sync --extra dev --frozen
uv run --frozen pytest benchmarks
```

Routine `uv run --frozen pytest` does not include benchmarks.

Run each case once without collecting timing statistics for a quicker
correctness check:

```bash
uv run --frozen pytest benchmarks --benchmark-disable
```

To measure only the smallest image size:

```bash
uv run --frozen pytest benchmarks -k 512x512
```

## Comparing changes

Save a run before changing performance-sensitive code:

```bash
uv run --frozen pytest benchmarks --benchmark-save=before
```

Run the same cases after the change and compare them with the saved result:

```bash
uv run --frozen pytest benchmarks --benchmark-compare
```

Saved results are written below `.benchmarks/`, which is ignored by Git. The
report includes the Git commit, Python runtime, machine information, repeated
measurements, and variability.

Use the same machine, power conditions, Python version, lockfile, and command
for both runs. Close unrelated CPU-intensive programs first. Results from
different environments are not directly comparable.
