# Import necessary libraries
import os
import tempfile

import numpy as np
import pytest

# Import the project-specific packages
from seamcarver.calculator import SeamCalculator
from seamcarver.core import SeamCarver


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    # Create a simple 3x3 RGB image with random colors
    return np.array(
        [
            [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
            [[128, 128, 0], [128, 0, 128], [0, 128, 128]],
            [[64, 64, 64], [192, 192, 192], [32, 32, 32]],
        ],
        dtype=np.uint8,
    )


@pytest.fixture
def calculator():
    """Create a SeamCalculator instance with a sample image."""
    return SeamCalculator()


@pytest.fixture
def carver(sample_image):
    """Create a SeamCarver instance with a sample image."""
    return SeamCarver(sample_image)


@pytest.fixture
def temp_output():
    """Provide temporary output file path."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
