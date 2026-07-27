# seamcarver

A Python package and command-line interface for content-aware image resizing with seam carving.

`seamcarver` removes low-information pixel paths (seams) instead of uniformly scaling or naively cropping, helping preserve visually important content. The implementation combines dynamic-programming seam search, pluggable energy functions, and a modular API/CLI architecture for experimentation and practical use.

## Additional Documentation

Detailed engineering documentation is available in the [`docs/`](docs/) directory:

- [Architecture Overview](docs/architecture.md)
- [Design Decisions](docs/design-decisions.md)
- [Optimization Notes](docs/optimization.md)
- [Benchmark Methodology](docs/benchmarking.md)
- [Algorithm Walkthrough](docs/algorithm-overview.md)

## Visual Examples

| Original | Resized (content-aware) |
| --- | --- |
| ![Original sample image](examples/medium.jpg) | ![Resized sample image](examples/medium_resized.jpg) |

| Seam Overlay |
| --- |
| ![Highlighted seams](examples/medium_seams.jpg) |

## Overview

Seam carving finds connected pixel paths with minimal cumulative energy and removes them iteratively to resize images while preserving salient structures. This repository provides:

- A functional Python API for integration into scripts and applications
- A stateful `SeamCarver` compatibility interface
- A CLI (`seamcarver`) for direct image processing workflows
- Extensible energy-method abstractions for algorithm experimentation
- A dynamic-programming seam computation pipeline that recalculates energy after
  each removal

## Features

- Content-aware image resizing via seam carving
- Vertical and horizontal seam removal
- Seam highlighting for visualization/debugging
- Pluggable energy methods:
  - `GradientEnergy`
  - `SobelEnergy`
  - `LaplacianEnergy`
- Dynamic-programming cumulative-cost computation and seam backtracking
- Iterative seam extraction and mask-based seam removal
- CLI logging controls: `--verbose`, `--quiet`, `--log-file`
- Python API and packaged distribution via `pyproject.toml`

## Installation

This beta is not published under this distribution name. The package named
`seamcarver` on PyPI is unrelated to this project.

Install a local checkout with standard Python tooling:

```bash
python -m pip install .
```

For development, install the locked environment with uv:

```bash
uv sync --extra dev --frozen
```

## Quick Start

```bash
seamcarver examples/medium.jpg resize 240 400 --output resized.jpg
```

## CLI Usage

```bash
seamcarver <input> <command> [options]
```

### Commands

- `resize <height> <width>`: resize image to target dimensions
- `remove --direction {vertical,horizontal} --count N`: remove `N` seams
- `highlight --direction {vertical,horizontal} --count N [--rgb R G B]`: highlight seams

### Common options

- `-o, --output <path>` optional output path; omit it to process without saving
- `-v, --verbose` debug-level logs
- `-q, --quiet` warnings/errors only
- `-l, --log-file <path>` write logs to file

## Library Usage

```python
import seamcarver

result = seamcarver.resize(
    "examples/medium.jpg",
    height=240,
    width=400,
    method=seamcarver.SobelEnergy(),
)
```

Request a reusable plan when a preview must show the exact pixels removed from
the result:

```python
resize_plan = seamcarver.plan(
    "examples/medium.jpg",
    height=240,
    width=400,
)

preview = resize_plan.highlight()
result = resize_plan.carve()
```

The stateful class remains available during the beta API migration:

```python
carver = seamcarver.SeamCarver("examples/medium.jpg")
carver.resize(height=240, width=400)
result = carver.image
```

## Architecture

### `SeamCarver` (`seamcarver/core.py`)

Compatibility interface for stateful image operations, saving, and display.

### Functional API (`seamcarver/core.py`)

`resize()` returns an owned transformed image. `plan()` computes reusable seam
decisions for matching carved and highlighted outputs.

### `SeamCalculator` (`seamcarver/calculator.py`)

Core algorithm layer that computes energy maps, builds cumulative DP cost tables, backtracks minimum seams, and returns seam masks for removal/highlighting.

### Energy interface + implementations (`seamcarver/methods/`)

`EnergyMethod` remains an optional abstract base class. The built-in
`GradientEnergy`, `SobelEnergy`, and `LaplacianEnergy` callables are
interchangeable.

### CLI layer (`seamcarver/cli.py`)

Argument parsing, command routing, logging setup, and operational error handling.

## Seam Carving Algorithm Overview

1. Compute an energy map from the current image.
2. Build cumulative minimum costs row-by-row with dynamic programming.
3. Backtrack from the lowest-cost endpoint to recover the minimum seam.
4. Convert seam locations into masks and remove/highlight seam pixels.
5. Repeat iteratively until the requested resize/removal target is reached.

## Energy Methods

- **GradientEnergy**: gradient-magnitude based pixel importance
- **SobelEnergy**: Sobel operator on grayscale image
- **LaplacianEnergy**: Laplacian operator on grayscale image

Custom methods may be plain functions, callable objects, or `EnergyMethod`
subclasses implementing `__call__(image) -> np.ndarray`.

## Optimization Notes

Current implementation includes several practical optimizations:

- Vectorized cumulative-cost updates in DP row transitions
- Transpose-based abstraction to unify horizontal/vertical seam logic
- Boolean-mask reshape strategy for seam removal
- Source-coordinate tracking across repeated seam removals

## Development

Install the locked development environment and run the repository checks:

```bash
uv sync --extra dev --frozen
uv run --frozen ruff check src tests benchmarks
uv run --frozen black --check --target-version py310 src tests benchmarks
uv run --frozen mypy
uv run --frozen pytest
```

## Benchmarking

The benchmark suite uses deterministic generated images and runs separately
from the unit tests:

```bash
uv run --frozen pytest benchmarks
```

See the [benchmark methodology](docs/benchmarking.md) for the measured cases
and comparison procedure.

## Repository Structure

- `seamcarver/core.py`  
  Public orchestration API for seam carving operations.
- `seamcarver/calculator.py`  
  Dynamic-programming seam search and seam-mask generation.
- `seamcarver/methods/`  
  Energy abstraction (`EnergyMethod`) and method implementations.
- `seamcarver/cli.py`  
  Command-line interface and operational logging.
- `seamcarver/constants.py`, `seamcarver/utils.py`, `seamcarver/logger.py`  
  Shared constants, helper utilities, and logging configuration.
- `tests/`  
  Unit/integration tests for API and CLI behavior.
- `benchmarks/`  
  Benchmark fixtures and performance test support.
- `examples/`  
  Sample images and generated visual outputs.

## Limitations

- Current implementation supports seam **removal** (not seam insertion/expansion).
- Quality depends on the selected energy method and image content.
- Extreme reductions can still introduce visual artifacts.

## Future Work

- Seam insertion for content-aware expansion
- Forward-energy variants and additional energy models
- Larger benchmark suite and published reference results
- Optional GPU/parallel acceleration experiments

## License

MIT License. See `LICENSE`.

## Attributions

- Algorithm concept: [Seam Carving (Wikipedia)](https://en.wikipedia.org/wiki/Seam_carving)
