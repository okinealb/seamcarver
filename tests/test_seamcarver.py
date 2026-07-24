"""
Unit tests for the SeamCarver class.

This module contains tests for the core functionality of the SeamCarver class,
including image resizing, seam removal, and exception handling. It ensures that
the seam carving algorithm behaves as expected when applied to sample images.

Components Tested:
- SeamCarver class:
  - Initialization and parameter handling.
  - Image resizing functionality.
  - Seam removal (vertical and horizontal).

Dependencies:
- numpy: Used to generate sample image data for testing.
- SeamCarver: The main class being tested.
- GradientEnergy: Default energy method used for testing.
- Constants (VERTICAL, HORIZONTAL): Used to specify seam directions.
"""

import numpy as np

# Import standard library packages
import pytest
from PIL import Image

from seamcarver.constants import HORIZONTAL, VERTICAL

# Import the project-specific packages
from seamcarver.core import SeamCalculator, SeamCarver


def test_load_from_array(sample_image):
    """Test loading an image from a numpy array."""
    carver = SeamCarver(sample_image)
    assert carver.image.shape == sample_image.shape
    assert isinstance(carver.image, np.ndarray)
    assert carver.verbose is False


def test_load_from_array_copies_input(sample_image):
    """The carver owns its image instead of aliasing caller state."""
    carver = SeamCarver(sample_image)

    sample_image[0, 0] = [1, 2, 3]

    assert not np.array_equal(carver.image[0, 0], sample_image[0, 0])


def test_load_from_list(sample_image):
    """Test loading an image from a nested list."""
    image_list = sample_image.tolist()
    carver = SeamCarver(image_list)
    assert carver.image.shape == sample_image.shape
    assert isinstance(carver.image, np.ndarray)
    assert carver.image.dtype == np.uint8
    assert carver.verbose is False


@pytest.mark.parametrize("mode", ["L", "RGBA"])
def test_load_from_pil_image_converts_to_rgb(mode):
    """PIL inputs are normalized to owned RGB uint8 arrays."""
    image_pil = Image.new(mode, (3, 2))
    carver = SeamCarver(image_pil)
    assert carver.image.shape == (2, 3, 3)
    assert carver.image.dtype == np.uint8


@pytest.mark.parametrize("use_path_object", [False, True])
def test_load_from_path(sample_image, tmp_path, use_path_object):
    """String and path-like inputs load through the same boundary."""
    image_path = tmp_path / "test_image.png"
    Image.fromarray(sample_image).save(image_path)
    image_input = image_path if use_path_object else str(image_path)
    carver = SeamCarver(image_input)

    assert carver.image.shape == sample_image.shape
    assert carver.image.dtype == np.uint8


def test_missing_path_raises_file_not_found(tmp_path):
    """Missing image paths retain the standard filesystem exception."""
    with pytest.raises(FileNotFoundError):
        SeamCarver(str(tmp_path / "missing.png"))


def test_undecodable_path_raises_value_error(tmp_path):
    """Existing files that are not images fail at the image boundary."""
    image_path = tmp_path / "invalid.png"
    image_path.write_bytes(b"not an image")

    with pytest.raises(ValueError, match="Could not decode image"):
        SeamCarver(str(image_path))


@pytest.mark.parametrize(
    "image",
    [
        np.zeros((3, 3), dtype=np.uint8),
        np.zeros((3, 3, 4), dtype=np.uint8),
        np.zeros((0, 3, 3), dtype=np.uint8),
        np.zeros((3, 0, 3), dtype=np.uint8),
        np.zeros((3, 3, 3), dtype=np.int64),
        np.zeros((3, 3, 3), dtype=np.float32),
    ],
)
def test_invalid_array_input_raises_value_error(image):
    """NumPy inputs must already satisfy the internal image contract."""
    with pytest.raises(ValueError):
        SeamCarver(image)


@pytest.mark.parametrize(
    "image",
    [
        [[[0, 0, 0], [0, 0]]],
        [[[-1, 0, 0]]],
        [[[256, 0, 0]]],
        [[[0.0, 0.0, 0.0]]],
        [],
    ],
)
def test_invalid_list_input_raises_value_error(image):
    """Nested-list inputs must be rectangular RGB bytes."""
    with pytest.raises(ValueError):
        SeamCarver(image)


def test_unsupported_input_type_raises_type_error():
    """Unsupported objects are distinguished from malformed image data."""
    with pytest.raises(TypeError):
        SeamCarver(object())


def test_initialization(carver, sample_image):
    """Test the initialization of the SeamCarver class."""
    assert carver.image.shape == sample_image.shape
    assert carver.verbose is False
    assert isinstance(carver.image, np.ndarray)
    assert isinstance(carver.calculator, SeamCalculator)


def test_resize_image(carver, sample_image):
    """Test the image resizing functionality."""
    shape = (
        sample_image.shape[0] - 1,
        sample_image.shape[1] - 1,
        sample_image.shape[2],
    )
    carver.resize(*shape[:2])
    assert carver.image.shape == shape


def test_highlight_image(carver):
    """Test the image highlighting functionality."""
    pytest.skip("Skipping seam removal tests as they are not implemented yet.")
    carver.highlight(VERTICAL)
    raise (NotImplementedError("Highlighting not implemented yet."))


def test_vertical_seam_removal(carver):
    """Test vertical seam removal."""
    original_shape = carver.shape
    carver.remove(num_seams=1, direction=VERTICAL)
    assert carver.image.shape[1] == original_shape[1] - 1
    assert carver.image.shape[0] == original_shape[0]


def test_horizontal_seam_removal(carver):
    """Test horizontal seam removal."""
    original_shape = carver.shape
    carver.remove(num_seams=1, direction=HORIZONTAL)
    assert carver.image.shape[0] == original_shape[0] - 1
    assert carver.image.shape[1] == original_shape[1]
