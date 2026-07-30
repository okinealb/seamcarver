import numpy as np

from seamop.methods import LaplacianEnergy


def test_returns_bounded_map(sample_image):
    energy = LaplacianEnergy()(sample_image)

    assert energy.shape == sample_image.shape[:2]
    assert np.issubdtype(energy.dtype, np.floating)
    assert np.all(energy >= 0)
    assert np.all(energy <= 1024)
