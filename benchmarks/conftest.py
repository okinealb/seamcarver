"""Shared fixtures for benchmarks."""

import pytest
import numpy as np
from PIL import Image
from pathlib import Path

@pytest.fixture(scope="session")
def sample_image():
    """Load sample image once per test session."""
    image_path = Path(__file__).parent.parent / "examples" / "sample.jpg"
    return np.array(Image.open(image_path).convert('RGB'))

@pytest.fixture(scope="function", params=[100, 1000, 10000])
def random_image(N):
    """Generate a random image of size (N, N, 3) for each test."""
    return np.random.randint(0, 256, (N, N, 3), dtype=np.uint8)