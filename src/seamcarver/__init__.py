"""Content-aware image resizing through seam carving.

Use :func:`resize` for an owned transformed image or :func:`plan` when the
same seam decisions must produce both a preview and a result.

    >>> import seamcarver
    >>> result = seamcarver.resize(image, height=150, width=200)
    >>> resize_plan = seamcarver.plan(image, height=150, width=200)
    >>> preview = resize_plan.highlight()

"""

from importlib.metadata import version as _distribution_version

# Expose the reusable plan result
from ._plan import ResizePlan

# Expose the seam calculator
from .calculator import SeamCalculator

# Expose public operations
from .core import plan, resize

# Import the energy interface and implemented methods
from .methods import EnergyMethod, GradientEnergy, LaplacianEnergy, SobelEnergy

__version__ = _distribution_version("seamcarver")

# Define the public API of this module
__all__ = [
    "ResizePlan",
    "resize",
    "plan",
    "SeamCalculator",
    "EnergyMethod",
    "GradientEnergy",
    "LaplacianEnergy",
    "SobelEnergy",
]
