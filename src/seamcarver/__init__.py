"""Content-aware image resizing by seam removal.

Use :func:`resize` for a transformed image or :func:`plan` when a preview and
result must share the same seam decisions.

>>> import numpy as np
>>> import seamcarver
>>> image = np.zeros((4, 5, 3), dtype=np.uint8)
>>> seamcarver.resize(image, height=3, width=4).shape
(3, 4, 3)
"""

from importlib.metadata import version as _distribution_version

from ._plan import ResizePlan
from .core import plan, resize
from .methods import GradientEnergy, LaplacianEnergy, SobelEnergy

__version__ = _distribution_version("seamcarver")

__all__ = [
    "ResizePlan",
    "resize",
    "plan",
    "GradientEnergy",
    "LaplacianEnergy",
    "SobelEnergy",
    "__version__",
]
