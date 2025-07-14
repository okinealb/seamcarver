"""
This module implements the Laplacian energy method for seam carving, providing
an energy map computation based on the Laplacian operator. The Laplacian
operator is widely used in image processing to detect regions of rapid
intensity change by calculating the second derivative at each pixel.

For more information, see the [Wikipedia article](https://en.wikipedia.org/wiki/Laplacian_of_Gaussian).
"""

# Import standard library packages
import numpy as np
from scipy.ndimage import laplace
# Import project specific packages
from .interface import EnergyMethod

class LaplacianEnergy(EnergyMethod):
    """Laplacian energy method for seam carving.
    
    This class implements the Laplacian operator to compute the energy map of an image.
    It inherits from the EnergyMethod interface.
    """

    def compute_energy(self, image) -> np.ndarray:
        """Compute the energy map of the image using the Laplacian operator."""
        # Convert the image to grayscale, then apply the Laplacian operator
        grayscale_image = np.mean(image, axis=2).astype(np.float32)
        laplacian_image = laplace(grayscale_image, mode='constant', cval=255)
        energy_tbl = np.abs(laplacian_image).astype(np.float16)
        
        return energy_tbl # Return the computed energy table