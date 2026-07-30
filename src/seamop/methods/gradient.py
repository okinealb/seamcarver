"""Color-gradient energy."""

import numpy as np
import numpy.typing as npt

from .interface import EnergyMethod

_BORDER_ENERGY = 1000


class GradientEnergy(EnergyMethod):
    """Compute color-gradient magnitude with protected image borders."""

    def __call__(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Return color-gradient energy for an RGB image."""
        energy_tbl = np.full(image.shape[:2], _BORDER_ENERGY, dtype=np.float32)
        image = image.astype(np.float32, copy=False)
        dx = image[1:-1, 2:] - image[1:-1, :-2]
        dy = image[2:, 1:-1] - image[:-2, 1:-1]
        energy_tbl[1:-1, 1:-1] = np.sqrt(
            np.sum(dx**2, axis=-1) + np.sum(dy**2, axis=-1)
        )

        return energy_tbl
