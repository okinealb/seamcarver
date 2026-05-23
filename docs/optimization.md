# Optimization Notes

This document summarizes optimization techniques currently present in the implementation and practical opportunities for future improvements.

## 1. Existing optimizations in code

### 1.1 Vectorized DP row updates

`_compute_costs` updates entire row slices at once instead of pixel-by-pixel Python loops for the interior region (`seamcarver/calculator.py:192-199`).  
This reduces Python overhead and keeps the hot path in NumPy operations.

### 1.2 Single-direction algorithm reuse via transpose

Horizontal seam operations reuse the vertical algorithm by transposing the image at the API boundary (`seamcarver/core.py:21-31`, `45-50`).  
This avoids maintaining and optimizing two separate seam-search implementations.

### 1.3 Multi-seam extraction with in-place invalidation

Within `_process`, energy is computed once and reused while extracting multiple seams; selected seam cells are invalidated with `np.inf` (`seamcarver/calculator.py:138-150`, `219`, `235`).  
This avoids full energy recomputation after every seam candidate.

### 1.4 Mask-based compaction

After seam selection, pixels are removed with boolean indexing + reshape (`seamcarver/calculator.py:118-122`, `seamcarver/core.py:145-148`).  
This is simple and vectorized relative to manual element shifts.

### 1.5 Memory-lean seam reconstruction

The algorithm tracks kept flat indices and reconstructs seam locations at the end, rather than storing every seam path separately (`seamcarver/calculator.py:106-107`, `121`, `123-127`).

## 2. Current optimization gaps

### 2.1 Batch-size heuristic is not currently applied

`batch_size` is computed in `__call__` using `MAP_DIMS_TO_SIZE` and `_get_batch_size`, but the value is not used to cap seam processing (`seamcarver/calculator.py:52-58`, `108-110`, `170-176`, `112-122`).

### 2.2 Recomputed cumulative-cost table per seam

Even when energy is reused within `_process`, cumulative costs are recomputed for each seam (`seamcarver/calculator.py:146`, `185-201`).  
This is correct and simple, but it is still a major cost center for large `num_seams`.

### 2.3 Float precision choices differ across stages

Energy methods use `float16` outputs (`seamcarver/methods/gradient.py:26`, `seamcarver/methods/sobel.py:26`, `29`, `seamcarver/methods/laplacian.py:26`, `28`), while cumulative costs use `float32` (`seamcarver/calculator.py:189`).  
This mixed-precision path balances memory and stability, but it should remain intentional and benchmarked.

## 3. Practical optimization opportunities

1. **Integrate real batching in `__call__`**  
   Use `batch_size` to bound seams processed per `_process` iteration, then compact and recompute energy in chunks (`seamcarver/calculator.py:108-110`, `112-122`, `129-155`, `170-176`).

2. **Reduce repeated full-table DP work**  
   Investigate incremental/local cost updates after seam invalidation, or selective recomputation windows around modified columns.

3. **Add benchmark baselines per method and image size**  
   Benchmark matrix should include method (`Gradient/Sobel/Laplacian`), resolution, seam count, and direction to identify true hotspots (`seamcarver/methods/__init__.py:30-39`, `seamcarver/core.py:136-160`).

4. **Profile memory allocations in seam loops**  
   Focus on repeated array creation in `_compute_costs`, mask unions, and reshape paths (`seamcarver/calculator.py:137`, `149`, `188-201`, `118-122`).

5. **Evaluate optional acceleration backends**  
   Candidates include JIT approaches for DP/backtracking loops or GPU-backed array libraries, guarded behind optional dependencies to preserve current API behavior.

## 4. Measurement guidance

When evaluating optimizations, track at least:

- wall-clock runtime for fixed `(H, W, num_seams, method, direction)`
- peak memory usage during seam loops
- output quality checks (visual artifact regression on sample images)
- numerical stability under different precisions

Use the repository’s pytest + benchmark setup to keep measurements comparable (see `[tool.pytest.ini_options]` and `[tool.pytest_benchmark]` in `pyproject.toml`).