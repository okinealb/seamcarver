"""
Unit tests for the SeamCalculator class.

This module contains tests for the core functionality of the SeamCalculator
class, including energy table, energy cost, and minimum seam computations.
It ensures that the seam carving algorithm behaves as expected when applied to
sample images.

Components Tested:
- SeamCalculator class:
  - Initialization and parameter handling.
  - Image resizing functionality.
  - Seam removal (vertical and horizontal).

Dependencies:
- numpy: Used to generate sample image data for testing.
- SeamCalculator: The main class being tested.
- GradientEnergy: Default energy method used for testing.
"""

# Import standard library packages
import numpy as np
import pytest

# Import the project-specific packages
from seamcarver.calculator import SeamCalculator
from seamcarver.methods import EnergyMethod, GradientEnergy


class FixedEnergy(EnergyMethod):
    """Return a fixed value for energy-boundary tests."""

    def __init__(self, output):
        self.output = output

    def __call__(self, image):
        return self.output


def test_initialization(calculator):
    """Test the initialization of the SeamCalculator class."""
    assert isinstance(calculator, SeamCalculator)
    assert isinstance(calculator.method, GradientEnergy)


def test_call(calculator, sample_image):
    """Test the seam finding functionality."""
    mask = calculator(sample_image, 1)
    # Shape and type checks
    assert mask.ndim == 2
    assert mask.shape == sample_image.shape[:2]
    assert np.issubdtype(mask.dtype, np.bool)
    assert mask.sum() == sample_image.shape[0]


def test_call_accepts_numpy_integer(calculator, sample_image):
    """NumPy integer seam counts follow Python's integer protocol."""
    mask = calculator(sample_image, np.int64(1))

    assert mask.sum() == sample_image.shape[0]


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
def test_invalid_num_seams(calculator, sample_image, num_seams, exception):
    """Direct calculator calls enforce the seam-count contract."""
    with pytest.raises(exception):
        calculator(sample_image, num_seams)


def test_compute_table(calculator, sample_image):
    """Test the energy table computation."""
    energy = calculator._compute_energy(sample_image)
    # Shape and type checks
    assert energy.shape == sample_image.shape[:2]
    assert np.issubdtype(energy.dtype, np.floating)
    # Value checks
    assert np.all(energy >= 0)


def test_compute_energy_normalizes_real_numeric_array(sample_image):
    """Accepted energy maps become owned float32 calculator state."""
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
)
def test_compute_energy_rejects_invalid_container_or_shape(
    sample_image, output, exception
):
    """Energy output must be a 2D NumPy array matching the image."""
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
)
def test_compute_energy_rejects_non_real_dtype(sample_image, output):
    """Boolean, complex, and text maps are not valid seam costs."""
    calculator = SeamCalculator(FixedEnergy(output))

    with pytest.raises(TypeError, match="real numeric"):
        calculator._compute_energy(sample_image)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf, np.finfo(float).max])
def test_compute_energy_rejects_nonfinite_float32_value(sample_image, value):
    """Values must remain finite in the calculator's float32 representation."""
    output = np.full((3, 3), value)
    calculator = SeamCalculator(FixedEnergy(output))

    with pytest.raises(ValueError, match="finite"):
        calculator._compute_energy(sample_image)


def test_compute_costs(calculator, sample_image):
    """Test the cost computation."""
    energy = calculator._compute_energy(sample_image)
    costs = calculator._compute_costs(energy)
    # Shape and type checks
    assert costs.shape == sample_image.shape[:2]
    assert np.issubdtype(costs.dtype, np.floating)
    # Value checks
    assert np.all(costs >= 0)


@pytest.mark.parametrize("sign", [-1, 1])
def test_compute_costs_keeps_finite_energy_finite(calculator, sign):
    """Finite float32 energy must not overflow during path accumulation."""
    energy = np.full(
        (3, 3),
        sign * np.finfo(np.float32).max,
        dtype=np.float32,
    )

    costs = calculator._compute_costs(energy)

    assert costs.dtype == np.float64
    assert np.isfinite(costs).all()


def test_compute_seams(calculator, sample_image):
    """Test the seam computation."""
    energy = calculator._compute_energy(sample_image)
    costs = calculator._compute_costs(energy)
    seams = calculator._compute_seams(energy, costs)
    # Shape and type checks
    assert seams.ndim == 2
    assert seams.shape == sample_image.shape[:2]
    # Value checks
    assert np.issubdtype(seams.dtype, np.bool)


def test_no_changes(calculator, sample_image):
    """Test that the original image is not modified."""
    original = sample_image.copy()

    calculator(sample_image, 1)

    assert np.array_equal(sample_image, original)


def test_call_fails_if_batch_makes_no_progress(calculator, sample_image, monkeypatch):
    """A stalled extraction fails instead of repeating forever."""
    no_seams = np.zeros(sample_image.shape[:2], dtype=bool)
    monkeypatch.setattr(
        calculator,
        "_process",
        lambda image, num_seams, batch_size: (0, no_seams),
    )

    with pytest.raises(RuntimeError, match="no progress"):
        calculator(sample_image, 1)
