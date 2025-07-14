"""
Tools for content-aware image resizing using the seam carving algorithm. It
exposes the `SeamCarver` class as the main interface, allowing users to
resize images while preserving important visual content.

Intended Usage:
---------------
Instantiate the `SeamCarver` class with the path to an image and an optional
`EnergyMethod` to define how pixel importance (energy) is calculated. The
package includes built-in energy methods such as `SobelEnergy` and
`LaplacianEnergy`, or users can implement their own by subclassing
`EnergyMethod`.

Example:

    carver = SeamCarver("path/to/image.jpg", energy_method=SobelEnergy())
    resized_image = carver.resize(width=200, height=150)
    resized_image.save("resized.jpg")

Modules:
--------
- core: Contains the `SeamCarver` class for performing seam carving operations.
- interfaces: Defines the `EnergyMethod` interface for custom energy calculations.
- method: Provides built-in energy calculation methods (e.g., Sobel, Laplacian).
"""

# Load metadata from the package
import importlib.metadata
metadata = importlib.metadata.metadata("seamcarver")
__version__ = metadata["Version"]
__summary__ = metadata["Summary"]
__license__ = metadata["License"]
__author__ = metadata["Author-email"]
__description__ = metadata["Description"]

# Import direction constants
from .constants import VERTICAL, HORIZONTAL

# Expose the main class
from .core import SeamCarver

# Import the energy interface and implemented methods
from .methods import EnergyMethod
from .methods import LaplacianEnergy, SobelEnergy, GradientEnergy
