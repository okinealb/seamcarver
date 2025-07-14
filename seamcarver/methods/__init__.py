"""
Energy Methods for Seam Carving

This package provides built-in energy calculation methods used in the seam
carving algorithm for content-aware image resizing. Energy methods determine
the importance of each pixel in an image, guiding which pixels are removed or
duplicated during resizing to preserve important visual content.

Available Energy Methods:
- `LaplacianEnergy`: Uses the Laplacian operator to highlight regions of rapid intensity change, making it effective for edge detection.
- `SobelEnergy`: Uses the Sobel operator to compute the gradient magnitude, emphasizing edges by measuring intensity changes in both horizontal and vertical directions.
- `GradientEnergy`: Computes the energy map based on image gradients, providing a measure of pixel importance based on local changes in intensity.

To use an energy method, instantiate it and pass it to the SeamCarver class.

Example:

    from seamcarver import SobelEnergy, LaplacianEnergy
    energy_method = SobelEnergy()
    # or
    energy_method = LaplacianEnergy()
"""

# Expose the interface
from .interface import EnergyMethod
# Expose the energy methods
from .laplacian import LaplacianEnergy
from .gradient import GradientEnergy
from .sobel import SobelEnergy