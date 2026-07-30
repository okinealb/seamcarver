# seamcarver

[![CI](https://github.com/okinealb/seamcarver/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/okinealb/seamcarver/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`seamcarver` is a Python library and command-line tool for content-aware image
resizing. It shrinks images by removing connected paths of low-energy pixels
instead of scaling every pixel or cropping a fixed region.

| Original | Planned removals | Resized |
| --- | --- | --- |
| ![Original image](examples/medium.jpg) | ![Highlighted seams](examples/medium_seams.jpg) | ![Resized image](examples/medium_resized.jpg) |

The current beta supports shrinking by seam removal. Enlargement and seam
insertion are not implemented.

## Installation

This project has not been published under its intended distribution name. The
package named `seamcarver` on PyPI is unrelated.

Install a local checkout with pip:

```bash
python -m pip install .
```

For development, use the locked uv environment:

```bash
uv sync --extra dev --frozen
```

## Command line

Resize the higher-resolution example to 1000 by 700 pixels:

```bash
seamcarver resize examples/large.jpg 1000 700
```

This writes `large_resized_1000x700.jpg` in the current directory. Use
`--output` to choose another path. Existing image outputs are not overwritten.

Preview the pixels that the same resize would remove:

```bash
seamcarver highlight examples/large.jpg 1000 700
```

Other commands and options are available through the built-in help:

```bash
seamcarver --help
seamcarver resize --help
seamcarver remove --help
seamcarver highlight --help
```

CLI dimensions use `WIDTH HEIGHT`.

## Python

`resize()` accepts a filesystem path, Pillow image, RGB `uint8` NumPy array, or
nested RGB integer list. It returns a new RGB `uint8` NumPy array without
mutating the input.

```python
from PIL import Image
import seamcarver

result = seamcarver.resize(
    "examples/large.jpg",
    width=1000,
    height=700,
)

Image.fromarray(result).save("large_resized_1000x700.jpg")
```

Use `plan()` when the carved result and preview must use the same seam
decisions:

```python
resize_plan = seamcarver.plan(
    "examples/large.jpg",
    width=1000,
    height=700,
)

preview = resize_plan.preview()
result = resize_plan.result()
```

Both output methods return independent arrays. Calling either method does not
change the plan.

See the [Python API guide](docs/api.md) for input rules, custom energy methods,
errors, and the advanced seam-calculation interface.

## Documentation

- [Python API](docs/api.md)
- [Algorithm overview](docs/algorithm-overview.md)
- [Architecture](docs/architecture.md)
- [Design decisions](docs/design-decisions.md)
- [Benchmarking](docs/benchmarking.md)

## Development

Run the repository checks from the project root:

```bash
uv run --frozen ruff check src tests benchmarks
uv run --frozen black --check --target-version py310 src tests benchmarks
uv run --frozen mypy
uv run --frozen pytest
uv run --frozen pytest --doctest-modules src/seamcarver
```

Benchmarks run separately:

```bash
uv run --frozen pytest benchmarks
```

## Limitations

- Only shrinking is supported.
- Width is reduced before height when both dimensions change.
- Results depend on the image and selected energy method.
- Large reductions can distort important content.

## License

[MIT](LICENSE)
