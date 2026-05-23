# Benchmark Results

This document records results from running:

```bash
python benchmarks/benchmark_seam_timing.py
```

The benchmark script generates random RGB images and measures elapsed time to remove vertical seams using `SeamCarver.remove(direction=VERTICAL, num_seams=...)`.

## Runtime Results (seconds)

| Image size | 10 seams | 20 seams | 40 seams | 80 seams | 160 seams |
| --- | ---: | ---: | ---: | ---: | ---: |
| Small (256x256) | 0.029 | 0.040 | 0.072 | 0.137 | 0.273 |
| Medium (512x512) | 0.071 | 0.107 | 0.183 | 0.330 | 0.651 |
| Large (1024x1024) | 0.213 | 0.291 | 0.470 | 0.836 | 1.569 |

## Observations

- Runtime increases as seam count increases for all image sizes.
- Larger images have higher absolute runtime at every seam count.
- Growth is roughly linear over the tested seam ranges.