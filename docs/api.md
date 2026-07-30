# Python API

The top-level API has two operations:

- `resize()` returns a resized image.
- `plan()` records one resize so its result and preview use the same seams.

Both operations create owned RGB `uint8` arrays and leave the source unchanged.

## Resize an image

```python
seamcarver.resize(image, *, height, width, method=seamcarver.GradientEnergy())
```

`image` may be:

- a filesystem path (`str` or `os.PathLike`)
- a Pillow image
- an RGB `uint8` NumPy array shaped `(height, width, 3)`
- a rectangular nested list of RGB integers from 0 through 255

Filesystem and Pillow inputs are converted to RGB. NumPy arrays must already
have the required shape and dtype. Numeric inputs are not silently clipped,
scaled, or stripped of channels.

`height` and `width` must be positive integers no larger than the source
dimensions. Both may equal their source dimension. Enlargement is rejected
because seam insertion is not implemented.

The return value is a new RGB `uint8` NumPy array:

```python
from PIL import Image
import seamcarver

result = seamcarver.resize(
    "examples/medium.jpg",
    width=400,
    height=240,
)

Image.fromarray(result).save("medium_resized_400x240.jpg")
```

When both dimensions shrink, `resize()` removes vertical seams first and then
horizontal seams. The order can affect the result and is currently fixed.

## Plan a resize

```python
seamcarver.plan(image, *, height, width, method=seamcarver.GradientEnergy())
```

`plan()` accepts the same inputs as `resize()` and returns a `ResizePlan`.
Planning performs the seam search immediately. The stored decisions can then
produce two outputs without repeating that work:

```python
resize_plan = seamcarver.plan(
    "examples/medium.jpg",
    width=400,
    height=240,
)

preview = resize_plan.preview()
result = resize_plan.result()
```

`result()` returns the carved image. `preview()` returns a source-sized image
with every planned removal colored red. Pass another RGB color when needed:

```python
preview = resize_plan.preview(color=(0, 255, 0))
```

The plan also reports its array shapes:

```python
print(resize_plan.source_shape)
print(resize_plan.target_shape)
```

`ResizePlan` keeps read-only internal arrays. `result()` and `preview()` return
new writable copies, so modifying an output does not change the plan.

Create plans with `seamcarver.plan()` rather than calling the `ResizePlan`
constructor.

## Energy methods

The default `GradientEnergy` method computes color-gradient magnitude. Two
grayscale alternatives are included:

- `SobelEnergy`
- `LaplacianEnergy`

Pass an instance through `method`:

```python
result = seamcarver.resize(
    "examples/medium.jpg",
    width=400,
    height=240,
    method=seamcarver.SobelEnergy(),
)
```

A custom method may be a function, callable object, or `EnergyMethod` subclass.
It receives an RGB `uint8` array and must return a finite, real, two-dimensional
NumPy array matching the image height and width:

```python
import numpy as np
import seamcarver


def red_channel_energy(image: np.ndarray) -> np.ndarray:
    return image[..., 0].astype(np.float32)


result = seamcarver.resize(
    "examples/medium.jpg",
    width=400,
    height=240,
    method=red_channel_energy,
)
```

The calculator validates every returned energy map before searching for a seam.
The command-line interface intentionally limits energy selection to the three
built-in methods.

## Advanced seam calculation

`SeamCalculator` exposes vertical seam selection for algorithm experiments:

```python
import numpy as np

from seamcarver.calculator import SeamCalculator

image = np.zeros((4, 5, 3), dtype=np.uint8)
mask = SeamCalculator()(image, num_seams=2)

assert mask.shape == image.shape[:2]
assert mask.sum() == 2 * image.shape[0]
```

Unlike the top-level operations, `SeamCalculator` accepts only an RGB `uint8`
NumPy array. It returns a boolean mask in the source image's coordinates and
does not mutate the array.

`EnergyMethod` remains available for class-based implementations:

```python
from seamcarver.methods import EnergyMethod
```

Subclassing it is optional because any compatible callable is accepted.

## Errors

The API reports invalid inputs before seam search:

| Condition | Error |
| --- | --- |
| Unsupported image type | `TypeError` |
| Invalid image shape, dtype, channels, or values | `ValueError` |
| Non-integer dimensions, seam counts, or color channels | `TypeError` |
| Zero, negative, or enlarged target dimensions | `ValueError` |
| Invalid energy-map type or dtype | `TypeError` |
| Invalid energy-map shape or non-finite values | `ValueError` |
| Missing or unreadable image path | `FileNotFoundError` or `ValueError` |

Operational errors do not expose a partial public result or mutate the source
input.
