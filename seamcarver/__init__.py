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

Basic Usage:
---------------
    >>> from seamcarver import SeamCarver, SobelEnergy
    >>> carver = SeamCarver("path/to/image.jpg", energy_method=SobelEnergy())
    >>> resized_image = carver.resize(width=200, height=150)
    >>> resized_image.save("resized.jpg")

Modules:
--------
- `core`: Contains the `SeamCarver` class for performing seam carving operations.
- `methods`: Defines the `EnergyMethod` interface and some energy table computation methods.
    - `EnergyMethod`: Interface for energy calculation methods.
    - `GradientEnergy`: Calculation using gradient magnitude.
    - `LaplacianEnergy`: Calculation using Laplacian filter.
    - `SobelEnergy`: Calculation using Sobel filter.
- `constants`: Contains constants used internally (`VERTICAL`, `HORIZONTAL`, `BORDER_ENERGY`).
- `calculator`: Contains the `SeamCalculator` class for seam calculation.

Architecture:
---------------
    The SeamCarver class handles both vertical and horizontal operations by
    transposing the image for horizontal seams. All other components assume
    vertical-only operations for simplicity.
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

# Define the public API of this module
__all__ = [
    "SeamCarver",
    "VERTICAL",
    "HORIZONTAL",
    "EnergyMethod",
    "GradientEnergy",
    "LaplacianEnergy",
    "SobelEnergy",
]