import numpy as np
import pytest
from PIL import Image

from seamcarver.calculator import SeamCalculator
from seamcarver.core import SeamCarver


@pytest.fixture
def sample_image():
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
    return SeamCalculator()


@pytest.fixture
def carver(sample_image):
    return SeamCarver(sample_image)


@pytest.fixture
def cli_image_path(tmp_path):
    image = np.arange(6 * 7 * 3, dtype=np.uint8).reshape(6, 7, 3)
    path = tmp_path / "input.png"
    Image.fromarray(image).save(path)
    return str(path)


@pytest.fixture
def output_path(tmp_path):
    return tmp_path / "output.png"
