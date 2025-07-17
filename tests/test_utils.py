"""
Unit tests for utility functions in the seamcarver package.

This module tests the utility functions provided in the seamcarver package,
ensuring that they produce correct outputs and handle edge cases. For example,
the `mask` function is tested for its ability to create pixel masks based on
seam indices.

Components Tested:
- Utility functions:
  - `mask`: Creates a mask for pixels to keep based on seam indices.

Dependencies:
- numpy: Used to generate sample data for testing.
- seamcarver.utils: The module containing utility functions being tested.
"""

# Import standard library packages
import pytest
import numpy as np
# Import the project specific packages
from seamcarver.utils import mask

@pytest.fixture
def sample_image():
    """Fixture to create a sample image for testing."""
    return np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[128, 128, 0], [128, 0, 128], [0, 128, 128]],
        [[64, 64, 64], [192, 192, 192], [32, 32, 32]]
    ], dtype=np.uint8)
    
def test_mask(sample_image):
    """Test the mask function for seam indices."""
    seam_indices = np.array([[0, 0], [1, 0], [2, 0]], dtype=int)
    result_mask = mask(seam_indices[:, 1], sample_image.shape[:2])
    
    # Expected mask should have False at seam indices and True elsewhere
    expected_mask = np.ones(sample_image.shape[:2], dtype=bool)
    for i, j in seam_indices:
        expected_mask[i, j] = False

    # Check if the result matches the expected mask
    assert np.array_equal(result_mask, expected_mask)