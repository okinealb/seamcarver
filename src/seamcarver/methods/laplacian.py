"""Grayscale Laplacian energy."""

from typing import cast

import numpy as np
import numpy.typing as npt
from scipy.ndimage import laplace

from .interface import EnergyMethod


class LaplacianEnergy(EnergyMethod):
    """Compute absolute grayscale Laplacian response."""

    def __call__(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Return Laplacian energy for an RGB image."""
        grayscale_image = np.mean(image, axis=2).astype(np.float32)
        laplacian_image = laplace(grayscale_image, mode="constant", cval=255)
        energy_tbl = np.abs(laplacian_image)

        return cast(npt.NDArray[np.float32], energy_tbl)
