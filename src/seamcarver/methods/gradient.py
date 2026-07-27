"""
This module implements the Gradient Magnitude energy method for seam carving,
providing an energy map computation based on image gradients. The image
gradient is commonly used in image processing to detect edges by calculating
the gradient magnitude at each pixel.

For more information, see the [Wikipedia article](https://en.wikipedia.org/wiki/Image_gradient).
"""

# Import standard library packages
import numpy as np
import numpy.typing as npt

# Import project-specific packages
from .interface import EnergyMethod

_BORDER_ENERGY = 1000


class GradientEnergy(EnergyMethod):
    """Gradient magnitude energy method for seam carving.

    This class implements image gradients to compute the energy map of an
    image. It inherits from the EnergyMethod interface.
    """

    def __call__(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Compute the energy map of the image using image gradients."""
        # Initialize the energy table with border values
        energy_tbl = np.full(image.shape[:2], _BORDER_ENERGY, dtype=np.float32)
        # Calculate gradients, then combine them for total energy
        image = image.astype(np.float32, copy=False)
        dx = image[1:-1, 2:] - image[1:-1, :-2]
        dy = image[2:, 1:-1] - image[:-2, 1:-1]
        energy_tbl[1:-1, 1:-1] = np.sqrt(
            np.sum(dx**2, axis=-1) + np.sum(dy**2, axis=-1)
        )

        return energy_tbl  # Return the computed energy table
