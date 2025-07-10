"""
This module implements the Sobel energy method for seam carving, providing an
energy map computation based on the Sobel operator. The Sobel operator is
commonly used in image processing to detect edges by calculating the
gradient magnitude at each pixel. 

For more information, see the [Wikipedia article](https://en.wikipedia.org/wiki/Sobel_operator).
"""

# Import standard library packages
import numpy as np
# Import project specific packages
from ..interfaces import EnergyMethod
from ..constants import VERTICAL, HORIZONTAL

class SobelEnergy(EnergyMethod):
    """Sobel energy method for seam carving.
    
    This class implements the Sobel operator to compute the energy map of an image.
    It inherits from the EnergyMethod interface.
    """

    def find_seam(self, image: np.ndarray, direction: int = VERTICAL) -> np.ndarray:
        """
        Find and return a directional seam as a list of indices.

        Parameters:
        - image (np.ndarray): The input image.
        - direction (int): The direction of the seam (VERTICAL or HORIZONTAL).

        Returns:
        - np.ndarray: The indices of the seam.
        """
        raise NotImplementedError("Sobel seam finding not implemented yet")

    def compute_energy(self, image: np.ndarray, direction: int = VERTICAL) -> np.ndarray:
        """
        Compute the energy map of the image using the Sobel operator.

        Parameters:
        - image (np.ndarray): The input image.
        - direction (int): The direction of the seam (VERTICAL or HORIZONTAL).

        Returns:
        - np.ndarray: The computed energy map.
        """
        raise NotImplementedError("Sobel energy computation not implemented yet")