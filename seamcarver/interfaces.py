"""
The abstract base class for energy methods in seam carving.

This module defines the `EnergyMethod` interface, which includes methods for
finding seams and computing energy maps. It serves as a blueprint for
implementing various energy calculation strategies in seam carving algorithms.
"""

# Import standard library packages
from abc import ABC, abstractmethod
import numpy as np
# Import project specific packages
from .core import VERTICAL

class EnergyMethod(ABC):
    """Base class for energy methods."""
    
    @abstractmethod
    def find_seam(self, image: np.ndarray, direction: int = VERTICAL) -> np.ndarray:
        """Find and return a directional seam as a list of indices."""
        pass
    
    @abstractmethod
    def compute_energy(self, image: np.ndarray, direction: int = VERTICAL) -> np.ndarray:
        """Compute the energy map of the image."""
        pass