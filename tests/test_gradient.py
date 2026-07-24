import numpy as np

from seamcarver.constants import BORDER_ENERGY
from seamcarver.methods import GradientEnergy


def test_returns_expected_map(sample_image):
    energy = GradientEnergy()(sample_image)

    assert energy.shape == sample_image.shape[:2]
    assert np.issubdtype(energy.dtype, np.floating)
    assert np.all(energy[:, 0] == BORDER_ENERGY)
    assert np.all(energy[0, :] == BORDER_ENERGY)
    assert np.all(energy[:, -1] == BORDER_ENERGY)
    assert np.all(energy[-1, :] == BORDER_ENERGY)
    assert np.all(energy[1:-1, 1:-1] >= 0)


def test_avoids_uint8_overflow():
    image = np.zeros((3, 3, 3), dtype=np.uint8)
    image[1, 2] = 240

    energy = GradientEnergy()(image)

    assert energy[1, 1] == np.float32(np.sqrt(3 * 240**2))
