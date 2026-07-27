import numpy as np
import pytest

from seamcarver.calculator import SeamCalculator
from seamcarver.constants import HORIZONTAL, VERTICAL
from seamcarver.core import SeamCarver


class FailingEnergy:
    """Raise on a selected call to test image-state recovery."""

    def __init__(self, fail_on_call=1):
        self.calls = 0
        self.fail_on_call = fail_on_call

    def __call__(self, image):
        self.calls += 1
        if self.calls == self.fail_on_call:
            raise RuntimeError("energy calculation failed")
        return np.zeros(image.shape[:2], dtype=float)


def test_uses_default_calculator(carver):
    assert isinstance(carver.calculator, SeamCalculator)


class TestResize:
    def test_updates_shape(self, carver, sample_image):
        target = (sample_image.shape[0] - 1, sample_image.shape[1] - 1)

        carver.resize(*target)

        assert carver.image.shape == (*target, 3)

    def test_matches_width_first_sequential_removal(self):
        image = np.arange(4 * 5 * 3, dtype=np.uint8).reshape(4, 5, 3)
        resized = SeamCarver(image)
        sequential = SeamCarver(image)

        resized.resize(3, 3)
        sequential.remove(VERTICAL, 2)
        sequential.remove(HORIZONTAL, 1)

        assert np.array_equal(resized.image, sequential.image)

    def test_same_shape_is_no_op(self, carver):
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
        ids=[
            "zero-height",
            "zero-width",
            "larger-height",
            "larger-width",
            "float-height",
            "bool-width",
        ],
    )
    def test_rejects_invalid_target(self, carver, height, width, exception):
        original = carver.image.copy()

        with pytest.raises(exception):
            carver.resize(height, width)

        assert np.array_equal(carver.image, original)

    def test_restores_image_after_failure(self, sample_image):
        carver = SeamCarver(sample_image, method=FailingEnergy(fail_on_call=2))
        original = carver.image.copy()

        with pytest.raises(RuntimeError, match="energy calculation failed"):
            carver.resize(2, 2)

        assert np.array_equal(carver.image, original)


@pytest.mark.parametrize(
    "direction", [VERTICAL, HORIZONTAL], ids=["vertical", "horizontal"]
)
def test_highlight_returns_independent_image(direction):
    carver = SeamCarver(np.zeros((3, 4, 3), dtype=np.uint8))
    color = [1, 2, 3]
    original = carver.image.copy()
    expected_pixels = carver.shape[0] if direction == VERTICAL else carver.shape[1]

    result = carver.highlight(direction, 1, color)

    assert result.shape == carver.shape
    assert result.dtype == carver.image.dtype
    assert np.all(result == color, axis=-1).sum() == expected_pixels
    assert np.array_equal(carver.image, original)
    assert result.flags.owndata
    assert not np.shares_memory(result, carver.image)


class TestRemove:
    def test_vertical_reduces_width(self, carver):
        original_shape = carver.shape

        carver.remove(VERTICAL, np.int64(1))

        assert carver.image.shape == (original_shape[0], original_shape[1] - 1, 3)

    def test_horizontal_reduces_height(self, carver):
        original_shape = carver.shape

        carver.remove(num_seams=1, direction=HORIZONTAL)

        assert carver.image.shape == (original_shape[0] - 1, original_shape[1], 3)

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
        ids=[
            "negative",
            "above-range",
            "string",
            "float",
            "bool",
            "numpy-bool",
        ],
    )
    def test_rejects_invalid_direction(self, carver, direction, exception):
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
        ids=[
            "negative",
            "zero",
            "equal-width",
            "over-width",
            "string",
            "float",
            "bool",
            "numpy-bool",
        ],
    )
    def test_rejects_invalid_count(self, carver, num_seams, exception):
        original = carver.image.copy()

        with pytest.raises(exception):
            carver.remove(VERTICAL, num_seams)

        assert np.array_equal(carver.image, original)

    def test_horizontal_count_uses_height(self):
        carver = SeamCarver(np.zeros((2, 4, 3), dtype=np.uint8))
        original = carver.image.copy()

        with pytest.raises(ValueError):
            carver.remove(HORIZONTAL, 2)

        assert np.array_equal(carver.image, original)

    def test_horizontal_failure_preserves_image(self, sample_image):
        carver = SeamCarver(sample_image, method=FailingEnergy())
        original = carver.image.copy()

        with pytest.raises(RuntimeError, match="energy calculation failed"):
            carver.remove(HORIZONTAL, 1)

        assert np.array_equal(carver.image, original)


def test_add_raises_not_implemented(carver):
    with pytest.raises(NotImplementedError, match="Seam addition"):
        carver.add(VERTICAL, 1)
