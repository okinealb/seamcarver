"""
Unit tests for the LaplacianEnergy method.

This module contains tests for the functionality of the LaplacianEnergy class,
including energy map computation. It ensures that the laplacian operator method
behaves as expected when applied to sample images.

Components Tested:
- LaplacianEnergy class:
  - Energy table calculation functionality.

Dependencies:
- numpy: Used to generate sample image data for testing.
- LaplacianEnergy: The main class being tested.
"""

# Import standard library packages
import pytest
import numpy as np
# Import the project-specific packages
from seamcarver.methods import LaplacianEnergy

@pytest.fixture
def sample_image():
    """Fixture to create a sample image for testing."""
    # Create a simple 3x3 RGB image with set colors
    return np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[128, 128, 0], [128, 0, 128], [0, 128, 128]],
        [[64, 64, 64], [192, 192, 192], [32, 32, 32]]
    ], dtype=np.uint8)

def test_energy_map(sample_image):
    """Test the energy map computation."""
    method = LaplacianEnergy()
    energy_tbl = method.compute_energy(sample_image)
    # Type and shape checks
    assert energy_tbl.shape == sample_image.shape[:2]
    assert np.issubdtype(energy_tbl.dtype, np.floating)
    # Ensure energy values are within range
    assert np.all(energy_tbl >= 0) and np.all(energy_tbl <= 1024)