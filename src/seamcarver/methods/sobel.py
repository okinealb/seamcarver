"""Grayscale Sobel energy."""

from typing import cast

import numpy as np
import numpy.typing as npt
from scipy.ndimage import sobel

from .interface import EnergyMethod


class SobelEnergy(EnergyMethod):
    """Compute grayscale Sobel-gradient magnitude."""

    def __call__(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Return Sobel-gradient energy for an RGB image."""
        grayscale_image = np.mean(image, axis=2).astype(np.float32)
        gradient_x = sobel(grayscale_image, axis=1, mode="constant", cval=255)
        gradient_y = sobel(grayscale_image, axis=0, mode="constant", cval=255)
        energy_tbl = np.sqrt(gradient_x**2 + gradient_y**2)

        return cast(npt.NDArray[np.float32], energy_tbl)
