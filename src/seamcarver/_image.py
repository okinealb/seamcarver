"""Internal image loading and normalization."""

import os
from typing import TypeAlias

import numpy as np
from PIL import Image

ImageInput: TypeAlias = np.ndarray | list | Image.Image | str | os.PathLike[str]


def normalize_image(image: ImageInput) -> np.ndarray:
    """Return an owned RGB uint8 array for a supported image input."""
    if isinstance(image, np.ndarray):
        return _from_ndarray(image)
    if isinstance(image, Image.Image):
        return _from_pillow_image(image)
    if isinstance(image, (str, os.PathLike)):
        return _from_path(image)
    if isinstance(image, list):
        return _from_nested_list(image)
    raise TypeError(
        "Image must be a NumPy array, nested list, PIL image, or filesystem path."
    )


def _from_ndarray(image: np.ndarray) -> np.ndarray:
    """Validate and copy an RGB uint8 array."""
    _validate_rgb_shape(image, "NumPy")
    if image.dtype != np.uint8:
        raise ValueError(f"NumPy image dtype must be uint8; received {image.dtype}.")
    return np.array(image, dtype=np.uint8, copy=True, order="C")


def _from_nested_list(image: list) -> np.ndarray:
    """Validate integer RGB data from a nested list."""
    try:
        array = np.asarray(image)
    except ValueError as error:
        raise ValueError("Nested-list image must be rectangular RGB data.") from error

    _validate_rgb_shape(array, "Nested-list")
    if not np.issubdtype(array.dtype, np.integer):
        raise ValueError("Nested-list image values must be integers from 0 to 255.")
    if np.any(array < 0) or np.any(array > 255):
        raise ValueError("Nested-list image values must be integers from 0 to 255.")
    return array.astype(np.uint8, copy=True)


def _from_pillow_image(image: Image.Image) -> np.ndarray:
    """Convert a Pillow image to an owned RGB uint8 array."""
    return np.array(image.convert("RGB"), dtype=np.uint8, copy=True)


def _from_path(path: str | os.PathLike[str]) -> np.ndarray:
    """Load a filesystem path as an owned RGB uint8 array."""
    try:
        with Image.open(path) as image:
            return _from_pillow_image(image)
    except FileNotFoundError:
        raise
    except (OSError, ValueError) as error:
        raise ValueError(f"Could not decode image from path: {path}") from error


def _validate_rgb_shape(image: np.ndarray, source: str) -> None:
    """Validate the dimensions required by the seam-carving implementation."""
    if image.ndim != 3:
        raise ValueError(
            f"{source} image must have shape (height, width, 3); "
            f"received {image.shape}."
        )
    if image.shape[2] != 3:
        raise ValueError(
            f"{source} image must have exactly 3 RGB channels; "
            f"received {image.shape[2]}."
        )
    if image.shape[0] == 0 or image.shape[1] == 0:
        raise ValueError(f"{source} image height and width must be greater than zero.")
