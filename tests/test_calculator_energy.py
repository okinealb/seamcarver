import numpy as np
import pytest

from seamcarver.calculator import SeamCalculator


class FixedEnergy:
    """Return a fixed map for energy-boundary tests."""

    def __init__(self, output):
        self.output = output

    def __call__(self, image):
        return self.output


class TestEnergyMap:
    def test_returns_float_map(self, calculator, sample_image):
        energy = calculator._compute_energy(sample_image)

        assert energy.shape == sample_image.shape[:2]
        assert np.issubdtype(energy.dtype, np.floating)
        assert np.all(energy >= 0)

    def test_owns_normalized_map(self, sample_image):
        output = np.arange(9, dtype=np.int16).reshape(3, 3) - 4
        energy = SeamCalculator(FixedEnergy(output))._compute_energy(sample_image)

        assert energy.dtype == np.float32
        assert np.array_equal(energy, output)

        energy[0, 0] = 100
        assert output[0, 0] == -4

    @pytest.mark.parametrize(
        ("output", "exception"),
        [
            ([[0, 0, 0]] * 3, TypeError),
            (np.zeros(3), ValueError),
            (np.zeros((3, 2)), ValueError),
            (np.zeros((3, 3, 1)), ValueError),
        ],
        ids=["list", "one-dimensional", "wrong-shape", "three-dimensional"],
    )
    def test_rejects_invalid_shape(self, sample_image, output, exception):
        calculator = SeamCalculator(FixedEnergy(output))

        with pytest.raises(exception):
            calculator._compute_energy(sample_image)

    @pytest.mark.parametrize(
        "output",
        [
            np.zeros((3, 3), dtype=bool),
            np.zeros((3, 3), dtype=complex),
            np.full((3, 3), "0"),
        ],
        ids=["bool", "complex", "string"],
    )
    def test_rejects_non_real_dtype(self, sample_image, output):
        calculator = SeamCalculator(FixedEnergy(output))

        with pytest.raises(TypeError, match="real numeric"):
            calculator._compute_energy(sample_image)

    @pytest.mark.parametrize(
        "value",
        [np.nan, np.inf, -np.inf, np.finfo(float).max],
        ids=["nan", "positive-inf", "negative-inf", "float64-max"],
    )
    def test_rejects_nonfinite_values(self, sample_image, value):
        output = np.full((3, 3), value)
        calculator = SeamCalculator(FixedEnergy(output))

        with pytest.raises(ValueError, match="finite"):
            calculator._compute_energy(sample_image)
