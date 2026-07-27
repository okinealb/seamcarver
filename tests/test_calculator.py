import numpy as np
import pytest

from seamcarver.calculator import SeamCalculator
from seamcarver.methods import GradientEnergy


def test_default_method_is_gradient(calculator):
    assert isinstance(calculator.method, GradientEnergy)


def test_mask_to_index_returns_flat_indices(calculator):
    mask = np.array(
        [
            [False, True, False],
            [True, False, True],
        ]
    )

    indices = calculator.mask_to_index(mask)

    assert np.array_equal(indices, [1, 3, 5])


class TestSeamCalculation:
    def test_accepts_numpy_integer(self, calculator, sample_image):
        mask = calculator(sample_image, np.int64(1))

        assert mask.sum() == sample_image.shape[0]

    @pytest.mark.parametrize(
        ("shape", "num_seams"),
        [
            ((1, 2), 1),
            ((2, 2), 1),
            ((3, 4), 2),
            ((4, 5), 3),
        ],
        ids=["single-row", "square", "two-seams", "three-seams"],
    )
    def test_returns_consistent_mask(self, shape, num_seams):
        height, _ = shape
        image = np.zeros((*shape, 3), dtype=np.uint8)

        mask = SeamCalculator()(image, num_seams)

        assert mask.shape == shape
        assert mask.dtype == np.bool_
        assert np.all(mask.sum(axis=1) == num_seams)
        assert mask.sum() == num_seams * height

        # A union mask only exposes individual connectivity for one seam.
        if num_seams == 1:
            columns = np.argmax(mask, axis=1)
            assert np.all(np.abs(np.diff(columns)) <= 1)

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
    def test_rejects_invalid_count(
        self, calculator, sample_image, num_seams, exception
    ):
        with pytest.raises(exception):
            calculator(sample_image, num_seams)

    def test_preserves_input(self, calculator, sample_image):
        original = sample_image.copy()

        calculator(sample_image, 1)

        assert np.array_equal(sample_image, original)

    def test_stops_without_progress(self, calculator, sample_image, monkeypatch):
        no_seams = np.zeros(sample_image.shape[:2], dtype=bool)
        monkeypatch.setattr(
            calculator,
            "_process",
            lambda image, num_seams, batch_size: (0, no_seams),
        )

        with pytest.raises(RuntimeError, match="no progress"):
            calculator(sample_image, 1)
