# Optimization Notes

This document outlines the performance-conscious decisions taken in the seamcarver implementation, and discusses the computational considerations, tradeoffs, and known bottlenecks.

## Vectorized Computation

- The core dynamic-programming (DP) updates through the image rows are implemented using NumPy vectorization. This allows each DP row to be updated in a single, batched operation for efficiency and minimal interpreter overhead.
- Boolean and floating-point arrays are used throughout, maximizing compatibility with NumPy's fast operations for masking, assignment, and accumulation.

## Unified Horizontal/Vertical Logic

- Rather than duplicating logic for horizontal and vertical seams, a transpose-based abstraction is used. This leverages NumPy's fast memory operations: for any direction, the same removal algorithm is applied, and the image/energy arrays are transposed as needed.

## Iterative Energy Recalculation

- The default algorithm recalculates energy after each seam removal because the
  removal changes neighboring pixels.
- Boolean masks remove seams, while a flat source-index map reconstructs their
  positions in the original image.

## Experimental Batching

- The private planner can reuse an energy map for more than one seam during
  controlled measurements.
- Batching is not selected automatically or exposed by the public API because it
  changes which pixels are removed.

## Profiling and Bottlenecks

- Repeated energy computation, dynamic programming, and image compaction account
  for the cost of multi-seam removal.
- Memory allocations are minimized where possible, but clarity is generally prioritized over low-level buffer reuse.
- Further speed improvements are possible by exploring in-place modifications and buffer pre-allocation, but have not yet been prioritized for clarity and maintainability.

## NumPy, Not Low-Level

- Instead of lower-level solutions or external libraries (OpenCV, C/C++), the project sticks with idiomatic NumPy for maximum readability and portability. This keeps dependencies light and makes contributions from users with basic Python knowledge possible.

## Opportunities for Future Optimization

- Forward-energy seam carving, GPU acceleration, or block-wise parallelism could
  be evaluated for high-resolution workloads.
- Advanced memory management or buffering strategies could reduce garbage generation and further optimize runtime memory locality.
- For now, the goal is to keep the code clean and transparent: any further optimizations will be implemented only when real-world bottlenecks appear in practical use cases.

Correctness remains the default. Performance changes require same-machine
measurements and must preserve the documented result contract unless an
alternative mode states otherwise.
