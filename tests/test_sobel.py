import numpy as np

from seamcarver.methods import SobelEnergy


def test_returns_bounded_map(sample_image):
    energy = SobelEnergy()(sample_image)

    assert energy.shape == sample_image.shape[:2]
    assert np.issubdtype(energy.dtype, np.floating)
    assert np.all(energy >= 0)
    assert np.all(energy <= 1024)
