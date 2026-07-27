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
  - The calculator validates each result and copies it to `float32`. This adds
    one full-map validation pass but keeps plugin errors out of the seam search.

## 3. Vertical-only seam logic with local orientation

**Decision:** Implement only the vertical seam algorithm and adapt horizontal
operations through a local transposed view.

- Evidence:
  - `_orient_image` normalizes an operation's local image view
    (`src/seamcarver/core.py`).
  - Comments explicitly stating downstream components assume vertical orientation (`seamcarver/core.py:45-50`; similar notes in `seamcarver/calculator.py:47-49`, `seamcarver/methods/interface.py:29-30`).
- Rationale:
  - Eliminates duplicate horizontal DP/backtracking implementations.
  - Centralizes direction handling in one place.
- Tradeoff:
  - Callers must convert completed horizontal results back to the stored
    orientation. Temporary orientation is not written to `self.image`.

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

## 6. Recompute energy after every seam

**Decision:** Public operations recompute the energy map after each seam removal.
The result therefore matches repeated one-seam calls.

- Rationale:
  - Removal changes pixel neighborhoods and may change their energy.
  - A hidden width-based batch heuristic made output depend on an undocumented
    performance policy.
- Tradeoff:
  - Batching reduces energy recomputation, but exploratory comparisons showed
    that it often selects different pixels.
  - Its performance benefit needs reproducible benchmark coverage before it can
    support a public speed claim.

## 7. Keep batching private

**Decision:** The planner retains an explicit private batch-size parameter for
measurement. The calculator does not expose it or select a batch size
automatically.

- Rationale:
  - This preserves the measured optimization without making an approximate mode
    part of the public contract.
- Revisit when:
  - A demonstrated use case justifies an explicit fast mode with documented
    output and quality expectations.
- Compatibility:
  - `SeamCalculator.MAP_DIMS_TO_SIZE` was removed without replacement because
    automatic batching is no longer supported.
  - The intended distribution remains unreleased. A version change will be
    chosen during release preparation rather than for this internal beta change.

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
