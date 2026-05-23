# Design Decisions and Tradeoffs

This document captures the major engineering decisions visible in the current implementation, why they were likely made, and tradeoffs.

## 1. Split orchestration from seam computation

**Decision:** Use `SeamCarver` for user-facing operations and `SeamCalculator` for algorithmic seam extraction.

- Evidence:
  - `SeamCarver` manages loading, operation sequencing, and I/O (`seamcarver/core.py:61-113`, `125-168`).
  - `SeamCalculator` owns DP seam search internals (`seamcarver/calculator.py:26-33`, `185-240`).
- Rationale:
  - Keeps computational core reusable and easier to test in isolation.
  - Prevents CLI/UI concerns from leaking into algorithm code.
- Tradeoff:
  - Slightly more indirection than a monolithic class.

## 2. Strategy interface for energy methods

**Decision:** Define abstract `EnergyMethod` and inject concrete methods.

- Evidence:
  - Interface contract (`seamcarver/methods/interface.py:13-35`).
  - Default and injected usage in both `SeamCarver` and `SeamCalculator` (`seamcarver/core.py:64`, `seamcarver/calculator.py:67`).
  - Built-ins: `GradientEnergy`, `SobelEnergy`, `LaplacianEnergy` (`seamcarver/methods/__init__.py:30-39`).
- Rationale:
  - Allows experimentation without changing seam search logic.
  - Supports research/benchmark use cases with interchangeable models.
- Tradeoff:
  - Energy methods must obey implicit assumptions (2D map shape, vertical orientation expectation in docs), but these are not strongly runtime-validated (`seamcarver/methods/interface.py:29-30`, `42-43`).

## 3. Vertical-only seam logic + transpose abstraction

**Decision:** Implement only vertical seam algorithm and adapt horizontal operations by transposing image state.

- Evidence:
  - `transpose_if_horizontal` decorator (`seamcarver/core.py:21-31`).
  - Comments explicitly stating downstream components assume vertical orientation (`seamcarver/core.py:45-50`; similar notes in `seamcarver/calculator.py:47-49`, `seamcarver/methods/interface.py:29-30`).
- Rationale:
  - Eliminates duplicate horizontal DP/backtracking implementations.
  - Centralizes direction handling in one place.
- Tradeoff:
  - Decorator mutates and restores `self.image`, which is elegant but stateful; debugging around failures inside wrapped methods can be more subtle.

## 4. NumPy-first implementation choices

**Decision:** Use NumPy arrays and vectorized operations as the primary computational model.

- Evidence:
  - Input normalization to NumPy arrays (`seamcarver/core.py:95-104`).
  - Vectorized DP row updates (`seamcarver/calculator.py:192-199`).
  - Boolean-mask removal + reshape (`seamcarver/core.py:146-148`).
- Rationale:
  - Good performance/clarity balance for Python numerical code.
  - Minimizes Python-level loops to seam-level control flow.
- Tradeoff:
  - Tight coupling to array shape conventions and dtype behavior (e.g., hardcoded RGB channel count `3` in reshapes) (`seamcarver/core.py:147`, `seamcarver/calculator.py:120`).

## 5. CLI and library dual interface

**Decision:** Provide both a command-line tool and importable Python API.

- Evidence:
  - CLI entrypoint in package metadata (`pyproject.toml:56-58`).
  - Public package exports for library usage (`seamcarver/__init__.py:64-72`).
- Rationale:
  - Supports end-users (CLI workflows) and developers/researchers (embedding in scripts).
- Tradeoff:
  - CLI currently prioritizes operational simplicity over full configurability (e.g., no argument for selecting energy method; default constructor path uses `GradientEnergy`) (`seamcarver/cli.py:93`, `seamcarver/core.py:64-65`).

## 6. Multi-seam extraction approach and implicit performance intent

**Decision:** In seam extraction loops, keep one energy table for a processing round and invalidate selected seam pixels with `np.inf` to continue selecting additional seams.

- Evidence:
  - `_process` computes energy once (`seamcarver/calculator.py:138-140`).
  - Each seam recomputes costs/backtracks and sets selected energy cells to `np.inf` (`seamcarver/calculator.py:146-150`, `219`, `235`).
- Likely rationale (implicit):
  - Reduce repeated energy recomputation overhead during multi-seam requests.
- Tradeoff:
  - Faster than fully recomputing energy after every removal, but can diverge from a strict “recompute-after-each-removal” interpretation.

## 7. Batch-size heuristic present but not currently integrated

**Observation/decision state:** The class defines width-to-batch mappings and computes `batch_size`, but current control flow does not use that value to constrain extraction loops.

- Evidence:
  - Heuristic table and helper (`seamcarver/calculator.py:52-58`, `170-176`).
  - Computed in `__call__` (`seamcarver/calculator.py:108-110`) without downstream use.
- Interpretation:
  - Suggests an optimization path that is incomplete, deferred, or retained from a prior implementation iteration.

## 8. Error handling and user feedback

**Decision:** Centralize CLI error messaging and logging policy.

- Evidence:
  - Logging setup with `verbose`, `quiet`, and optional file handler (`seamcarver/logger.py:8-63`).
  - `handle_error` maps exception categories to user-oriented messaging (`seamcarver/cli.py:130-160`).
- Rationale:
  - Improves UX for command-line users by providing actionable diagnostics.
- Tradeoff:
  - Some detail is intentionally hidden unless `--verbose` is set (`seamcarver/cli.py:156-159`).

## 9. Rejected alternatives (explicit vs implicit)

- **No explicit ADR/rejected-alternatives record** was found in the repository docs; rationale is mostly inferred from code comments and structure.
- **Implicitly rejected by architecture shape:**
  1. Separate horizontal algorithm implementation, in favor of transpose reuse (`seamcarver/core.py:21-31`, `45-50`).
  2. Single hardcoded energy model, in favor of strategy abstraction (`seamcarver/methods/interface.py:13-35`).
  3. CLI-only design, in favor of dual CLI + API distribution (`pyproject.toml:56-58`, `seamcarver/__init__.py:64-72`).