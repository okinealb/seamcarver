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
import pytest
import numpy as np
# Import the project specific packages
from seamcarver.calculator import SeamCalculator
from seamcarver.methods import GradientEnergy
from seamcarver.constants import VERTICAL, HORIZONTAL

@pytest.fixture
def sample_image():
    """Fixture to create a sample image for testing."""
    # Create a simple 3x3 RGB image with random colors
    return np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[128, 128, 0], [128, 0, 128], [0, 128, 128]],
        [[64, 64, 64], [192, 192, 192], [32, 32, 32]]
    ], dtype=np.uint8)

@pytest.fixture
def calculator(sample_image):
    """Fixture to create a SeamCalculator instance with a sample image."""
    return SeamCalculator(sample_image, method=GradientEnergy())

def test_initialization(calculator, sample_image):
    """Test the initialization of the SeamCalculator class."""
    assert calculator.image.shape == sample_image.shape
    assert isinstance(calculator.image, np.ndarray)
    assert isinstance(calculator.method, GradientEnergy)

def test_find_seam(calculator):
    """Test the seam finding functionality."""
    seam = calculator.find_seam()
    # Shape and type checks
    assert len(seam) == calculator.image.shape[0]
    assert seam.ndim == 1
    assert np.issubdtype(seam.dtype, np.integer)
    
def test_compute_table(calculator):
    """Test the energy table computation."""
    calculator._compute_energy()
    # Shape and type checks
    assert calculator.energy_tbl.shape == calculator.image.shape[:2]
    assert np.issubdtype(calculator.energy_tbl.dtype, np.floating)
    # Value checks
    assert np.all(calculator.energy_tbl >= 0)
    
def test_compute_cost(calculator, sample_image):
    """Test the cost computation."""
    calculator._compute_energy()
    calculator._compute_cost()
    # Shape and type checks
    assert calculator.energy_cst.shape == sample_image.shape[:2]
    assert np.issubdtype(calculator.energy_cst.dtype, np.floating)
    # Value checks
    assert np.all(calculator.energy_cst >= 0)

def test_compute_seam(calculator):
    """Test the seam computation."""
    calculator._compute_energy()
    calculator._compute_cost()
    calculator._compute_seam()
    # Shape and type checks
    assert len(calculator.seam) == calculator.image.shape[0]
    assert calculator.seam.ndim == 1
    # Value checks
    assert np.issubdtype(calculator.seam.dtype, np.integer)