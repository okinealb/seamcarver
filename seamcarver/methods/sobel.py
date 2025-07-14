"""
This module implements the Sobel energy method for seam carving, providing an
energy map computation based on the Sobel operator. The Sobel operator is
commonly used in image processing to detect edges by calculating the
gradient magnitude at each pixel. 

For more information, see the [Wikipedia article](https://en.wikipedia.org/wiki/Sobel_operator).
"""

# Import standard library packages
import numpy as np
from scipy.ndimage import sobel
# Import project specific packages
from .interface import EnergyMethod

class SobelEnergy(EnergyMethod):
    """Sobel energy method for seam carving.
    
    This class implements the Sobel operator to compute the energy map of an
    image. It inherits from the EnergyMethod interface.
    """

    def compute_energy(self, image) -> np.ndarray:
        """Compute the energy map of the image using the Sobel operator."""
        # Convert the image to grayscale, then apply the Sobel operator
        grayscale_image = np.mean(image, axis=2).astype(np.float32)
        gradient_x = sobel(grayscale_image, axis=1, mode='constant', cval=255)
        gradient_y = sobel(grayscale_image, axis=0, mode='constant', cval=255)
        energy_tbl = np.sqrt(gradient_x**2 + gradient_y**2).astype(np.float16)
        
        return energy_tbl # Return the computed energy table