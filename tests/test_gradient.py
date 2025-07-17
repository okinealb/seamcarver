"""
Unit tests for the GradientEnergy method.

This module contains tests for the functionality of the GradientEnergy class,
including energy map computation. It ensures that the gradient energy method
behaves as expected when applied to sample images.

Components Tested:
- GradientEnergy class:
  - Energy table calculation functionality.

Dependencies:
- numpy: Used to generate sample image data for testing.
- GradientEnergy: The main class being tested.
- Constants (BORDER_ENERGY): Used to define border energy values.
"""

# Import standard library packages
import pytest
import numpy as np
# Import the project specific packages
from seamcarver.methods import GradientEnergy
from seamcarver.constants import BORDER_ENERGY

@pytest.fixture
def sample_image():
    """Fixture to create a sample image for testing."""
    # Create a simple 5x5 RGB image with random colors
    return np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[128, 128, 0], [128, 0, 128], [0, 128, 128]],
        [[64, 64, 64], [192, 192, 192], [32, 32, 32]]
    ], dtype=np.uint8)

def test_energy_map(sample_image):
    """Test the energy map computation."""
    method = GradientEnergy()
    energy_tbl = method.compute_energy(sample_image)
    # Type and shape checks
    assert energy_tbl.shape == sample_image.shape[:2]
    assert np.issubdtype(energy_tbl.dtype, np.floating)
    # Border energy checks
    assert np.all(energy_tbl[:,0] == BORDER_ENERGY)
    assert np.all(energy_tbl[0,:] == BORDER_ENERGY)
    assert np.all(energy_tbl[:,-1] == BORDER_ENERGY)
    assert np.all(energy_tbl[-1,:] == BORDER_ENERGY)
    # Internal energy checks
    assert np.all(0 <= energy_tbl[1:-1, 1:-1] <= 255)