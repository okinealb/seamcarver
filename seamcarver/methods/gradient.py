"""
This module implements the Gradient Magnitude energy method for seam carving,
providing an energy map computation based on image gradients. The image
gradient is commonly used in image processing to detect edges by calculating
the gradient magnitude at each pixel. 

For more information, see the [Wikipedia article](https://en.wikipedia.org/wiki/Image_gradient).
"""

# Import standard library packages
import numpy as np
# Import project specific packages
from .interface import EnergyMethod
from ..constants import BORDER_ENERGY

class GradientEnergy(EnergyMethod):
    """Gradient magnitude energy method for seam carving.
    
    This class implements image gradients to compute the energy map of an
    image. It inherits from the EnergyMethod interface.
    """

    def compute_energy(self, image: np.ndarray) -> np.ndarray:
        """Compute the energy map of the image using image gradients."""
        # Initialize the energy table with border values
        energy_tbl = np.full(image.shape[:2], BORDER_ENERGY, dtype=np.float16)
        # Calculate gradients, then combine them for total energy
        dx = (image[1:-1, 2:] - image[1:-1, :-2])
        dy = (image[2:, 1:-1] - image[:-2, 1:-1])
        energy_tbl[1:-1, 1:-1] = np.sqrt(np.sum(dx**2, axis=2) + np.sum(dy**2, axis=2))
        
        return energy_tbl # Return the computed energy table