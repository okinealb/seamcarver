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
from seamcarver.methods import EnergyMethod


class FailingEnergy(EnergyMethod):
    """Energy method used to verify image-state recovery."""

    def __init__(self, fail_on_call=1):
        self.calls = 0
        self.fail_on_call = fail_on_call

    def __call__(self, image):
        self.calls += 1
        if self.calls == self.fail_on_call:
            raise RuntimeError("energy calculation failed")
        return np.zeros(image.shape[:2], dtype=float)


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


def test_resize_to_current_shape_is_no_op(carver):
    """An unchanged target does not invoke seam removal."""
    original = carver.image.copy()

    carver.resize(np.int64(carver.shape[0]), np.int64(carver.shape[1]))

    assert np.array_equal(carver.image, original)


@pytest.mark.parametrize(
    ("height", "width", "exception"),
    [
        (0, 2, ValueError),
        (2, 0, ValueError),
        (4, 2, ValueError),
        (2, 4, ValueError),
        (2.0, 2, TypeError),
        (2, True, TypeError),
    ],
)
def test_invalid_resize_target_leaves_image_unchanged(carver, height, width, exception):
    """Resize validates the entire request before changing image state."""
    original = carver.image.copy()

    with pytest.raises(exception):
        carver.resize(height, width)

    assert np.array_equal(carver.image, original)


def test_resize_failure_restores_original_image(sample_image):
    """A failure after one directional removal rolls back the resize."""
    carver = SeamCarver(sample_image, method=FailingEnergy(fail_on_call=2))
    original = carver.image.copy()

    with pytest.raises(RuntimeError, match="energy calculation failed"):
        carver.resize(2, 2)

    assert np.array_equal(carver.image, original)


def test_highlight_image_accepts_positional_arguments(carver):
    """Highlight preserves its declared positional call form."""
    color = [1, 2, 3]

    carver.highlight(VERTICAL, 1, color)

    highlighted = np.all(carver.image == color, axis=-1)
    assert highlighted.sum() == carver.shape[0]


def test_vertical_seam_removal(carver):
    """Test vertical seam removal."""
    original_shape = carver.shape
    carver.remove(VERTICAL, np.int64(1))
    assert carver.image.shape[1] == original_shape[1] - 1
    assert carver.image.shape[0] == original_shape[0]


def test_horizontal_seam_removal(carver):
    """Test horizontal seam removal."""
    original_shape = carver.shape
    carver.remove(num_seams=1, direction=HORIZONTAL)
    assert carver.image.shape[0] == original_shape[0] - 1
    assert carver.image.shape[1] == original_shape[1]


@pytest.mark.parametrize(
    ("direction", "exception"),
    [
        (-1, ValueError),
        (2, ValueError),
        ("vertical", TypeError),
        (1.0, TypeError),
        (True, TypeError),
        (np.bool_(False), TypeError),
    ],
)
def test_invalid_direction_leaves_image_unchanged(carver, direction, exception):
    """Invalid directions fail before image processing."""
    original = carver.image.copy()

    with pytest.raises(exception):
        carver.remove(direction, 1)

    assert np.array_equal(carver.image, original)


@pytest.mark.parametrize(
    ("num_seams", "exception"),
    [
        (-1, ValueError),
        (0, ValueError),
        (3, ValueError),
        (4, ValueError),
        ("1", TypeError),
        (1.0, TypeError),
        (True, TypeError),
        (np.bool_(True), TypeError),
    ],
)
def test_invalid_seam_count_leaves_image_unchanged(carver, num_seams, exception):
    """Invalid seam counts fail without changing image state."""
    original = carver.image.copy()

    with pytest.raises(exception):
        carver.remove(VERTICAL, num_seams)

    assert np.array_equal(carver.image, original)


def test_horizontal_count_uses_image_height():
    """Horizontal count bounds apply to rows, not columns."""
    carver = SeamCarver(np.zeros((2, 4, 3), dtype=np.uint8))
    original = carver.image.copy()

    with pytest.raises(ValueError):
        carver.remove(HORIZONTAL, 2)

    assert np.array_equal(carver.image, original)


def test_horizontal_failure_leaves_image_unchanged(sample_image):
    """Horizontal processing never stores a temporary transposed state."""
    carver = SeamCarver(sample_image, method=FailingEnergy())
    original = carver.image.copy()

    with pytest.raises(RuntimeError, match="energy calculation failed"):
        carver.remove(HORIZONTAL, 1)

    assert np.array_equal(carver.image, original)


def test_add_is_explicitly_not_implemented(carver):
    """Seam addition remains deferred instead of failing incidentally."""
    with pytest.raises(NotImplementedError, match="Seam addition"):
        carver.add(VERTICAL, 1)
