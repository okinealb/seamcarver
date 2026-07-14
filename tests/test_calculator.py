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
# Import the project-specific packages
from seamcarver.calculator import SeamCalculator
from seamcarver.methods import GradientEnergy


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
    
    # TODO: Check there are as many seams as requested
    
def test_compute_table(calculator, sample_image):
    """Test the energy table computation."""
    energy = calculator._compute_energy(sample_image)
    # Shape and type checks
    assert energy.shape == sample_image.shape[:2]
    assert np.issubdtype(energy.dtype, np.floating)
    # Value checks
    assert np.all(energy >= 0)
    
def test_compute_costs(calculator, sample_image):
    """Test the cost computation."""
    energy = calculator._compute_energy(sample_image)
    costs = calculator._compute_costs(energy)
    # Shape and type checks
    assert costs.shape == sample_image.shape[:2]
    assert np.issubdtype(costs.dtype, np.floating)
    # Value checks
    assert np.all(costs >= 0)

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
    
def test_no_changes(calculator):
    """Test that the original image is not modified."""
    
    # TODO: CHECK THE IMAGE IS NOT MODIFIED