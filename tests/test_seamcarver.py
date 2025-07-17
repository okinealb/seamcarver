"""
Unit tests for the SeamCarver class.

This module contains tests for the core functionality of the SeamCarver class,
including image resizing, seam removal, and exception handling. It ensures that
the seam carving algorithm behaves as expected when applied to sample images.

Components Tested:
- SeamCarver class:
  - Initialization and parameter handling.
  - Image resizing functionality.
  - Seam removal (vertical and horizontal).

Dependencies:
- numpy: Used to generate sample image data for testing.
- SeamCarver: The main class being tested.
- GradientEnergy: Default energy method used for testing.
- Constants (VERTICAL, HORIZONTAL): Used to specify seam directions.
"""

# Import standard library packages
import pytest
import numpy as np
from PIL import Image
import os
# Import the project specific packages
from seamcarver.core import SeamCarver, SeamCalculator
from seamcarver.methods import GradientEnergy
from seamcarver.constants import VERTICAL, HORIZONTAL

@pytest.fixture
def sample_image():
    """Fixture to create a sample image for testing."""
    return np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[128, 128, 0], [128, 0, 128], [0, 128, 128]],
        [[64, 64, 64], [192, 192, 192], [32, 32, 32]]
    ], dtype=np.uint8)
    
@pytest.fixture
def carver(sample_image):
    """Fixture to create a SeamCarver instance with a sample image."""
    return SeamCarver(sample_image, method=GradientEnergy())

def test_load_from_array(sample_image):
    """Test loading an image from a numpy array."""
    image = sample_image
    carver = SeamCarver(image)
    assert carver.image.shape == sample_image.shape
    assert isinstance(carver.image, np.ndarray)
    
def test_load_from_list(sample_image):
    """Test loading an image from a nested list."""
    image = sample_image.tolist()
    carver = SeamCarver(image)
    assert carver.image.shape == sample_image.shape
    assert isinstance(carver.image, np.ndarray)
    
def test_load_from_pil_image(sample_image):
    """Test loading an image from a PIL Image object."""
    image = Image.fromarray(sample_image)
    carver = SeamCarver(image)
    assert carver.image.shape == sample_image.shape
    assert isinstance(carver.image, np.ndarray)
    
def test_load_from_path(sample_image):
    """Test loading an image from a file path."""
    # Create a temporary image file for testing
    image = Image.fromarray(sample_image)
    image_path = "tests/test_image.png"
    image.save(image_path)
    carver = SeamCarver(image_path)
    # Shape and type checks
    assert carver.image.shape == sample_image.shape
    assert isinstance(carver.image, np.ndarray)
    # Clean up the temporary file
    os.remove(image_path)

def test_initialization(carver, sample_image):
    """Test the initialization of the SeamCarver class."""
    assert carver.image.shape == sample_image.shape
    assert carver.verbose is False
    assert isinstance(carver.image, np.ndarray)
    assert isinstance(carver.calculator, SeamCalculator)
    
def test_resize_image(carver, sample_image):
    """Test the image resizing functionality."""
    shape = (sample_image.shape[0] - 1, sample_image.shape[1] - 1, sample_image.shape[2])
    carver.resize(*shape[:2])
    assert carver.image.shape == shape
    
# def test_highlight_image(carver):
#     """Test the image highlighting functionality."""
#     carver.highlight(VERTICAL)
#     raise(NotImplementedError("Highlighting not implemented yet."))
    
def test_vertical_seam_removal(carver):
    """Test vertical seam removal."""
    original_shape = carver.shape
    carver.remove(num_seams = 1 , direction = VERTICAL)
    assert carver.image.shape[1] == original_shape[1] - 1
    assert carver.image.shape[0] == original_shape[0]
    
def test_horizontal_seam_removal(carver):
    """Test horizontal seam removal."""
    original_shape = carver.shape
    carver.remove(num_seams = 1 , direction = HORIZONTAL)
    assert carver.image.shape[0] == original_shape[0] - 1
    assert carver.image.shape[1] == original_shape[1]