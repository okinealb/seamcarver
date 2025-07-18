"""
The abstract base class for energy methods in seam carving.

This module defines the `EnergyMethod` interface, which includes methods for
finding seams. It serves as a blueprint for implementing various energy
calculation strategies in seam carving algorithms.
"""

# Import standard library packages
from abc import ABC, abstractmethod
import numpy as np

class EnergyMethod(ABC):
    """Base class for energy table computation methods.
    
    This abstract base class defines the interface for computing energy maps
    in seam carving algorithms. Subclasses must implement the `compute_energy`
    method to provide specific energy calculation strategies.
    
    Examples:
        >>> class CustomEnergy(EnergyMethod):
        ...     def compute_energy(self, image: np.ndarray) -> np.ndarray:
        ...         return np.random.random(image.shape[:2])
        
    Note: This class assumes that the image is always in a vertical orientation
    for seam carving. For horizontal seams, the image should be transposed
    before passing it to the methods.
    """
    
    @abstractmethod
    def compute_energy(self, image: np.ndarray) -> np.ndarray:
        """Compute the energy map of the image.
        
        Args:
            image (np.ndarray): Input image as a 3D numpy array (height, width, channels).
            
        Returns:
            Energy map as a 2D numpy array (height, width) where higher
            values indicate more important pixels.
        """
        pass