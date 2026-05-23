# Optimization Notes

This document outlines the performance-conscious decisions taken in the seamcarver implementation, and discusses the computational considerations, tradeoffs, and known bottlenecks.

## Vectorized Computation

- The core dynamic-programming (DP) updates through the image rows are implemented using NumPy vectorization. This allows each DP row to be updated in a single, batched operation for efficiency and minimal interpreter overhead.
- Boolean and floating-point arrays are used throughout, maximizing compatibility with NumPy's fast operations for masking, assignment, and accumulation.

## Unified Horizontal/Vertical Logic

- Rather than duplicating logic for horizontal and vertical seams, a transpose-based abstraction is used. This leverages NumPy's fast memory operations: for any direction, the same removal algorithm is applied, and the image/energy arrays are transposed as needed.

## In-Place Seam Invalidation

- During multi-seam extraction, seam locations are invalidated in-place by setting their positions to `np.inf` (or otherwise marking them), avoiding the need to recompute the full energy table or create new masks for every seam.
- Boolean masks are used for seam removal, reshaped as necessary to efficiently remove entire seams from the NP arrays without unnecessary copying.

## Adaptive Batching

- For very large images or when many seams are extracted, an adaptive batch sizing logic is applied: a fixed proportion of the image width may be targeted in a single operation before the energy table is rebuilt.
- This approach sacrifices some per-seam optimality for a substantial win in speed, as full energy recomputation is rate-limiting.

## Profiling and Bottlenecks

- Energy map computation remains the largest time sink, as it requires per-pixel calculations across the full image. Batch extraction and mask-based removals streamline the remainder of the operation.
- Memory allocations are minimized where possible, but clarity is generally prioritized over low-level buffer reuse.
- Further speed improvements are possible by exploring in-place modifications and buffer pre-allocation, but have not yet been prioritized for clarity and maintainability.

## NumPy, Not Low-Level

- Instead of lower-level solutions or external libraries (OpenCV, C/C++), the project sticks with idiomatic NumPy for maximum readability and portability. This keeps dependencies light and makes contributions from users with basic Python knowledge possible.

## Opportunities for Future Optimization

- Forward-energy seam carving, GPU acceleration (with CuPy or numba), or block-wise parallelism could yield further gains, especially for batch or high-resolution workloads.
- Advanced memory management or buffering strategies could reduce garbage generation and further optimize runtime memory locality.
- For now, the goal is to keep the code clean and transparent: any further optimizations will be implemented only when real-world bottlenecks appear in practical use cases.

## Summary

I consciously favor readable, well-structured NumPy code over micro-optimized or highly specialized code. The key performance win comes from batch processing and vectorization, which provides “good enough” speed on commodity hardware for typical use cases.