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
    """Base class for energy computation methods.
    
    This abstract base class defines the interface for computing energy maps
    in seam carving algorithms. Energy methods are callable objects that
    transform images into importance maps for guiding seam placement.
    
    Examples:
        >>> class CustomEnergy(EnergyMethod):
        ...     def __call__(self, image: np.ndarray) -> np.ndarray:
        ...         return np.random.random(image.shape[:2])
        ...
        >>> method = CustomEnergy()
        >>> energy_map = method(image)
        
    Note: 
        This class assumes vertical seam orientation. For horizontal 
        seams, transpose the image before passing to the method.
    """
    
    @abstractmethod
    def __call__(self, image: np.ndarray) -> np.ndarray:
        """Compute energy map indicating pixel importance.
        
        Args:
            image: Input image as 3D numpy array (height, width, channels).
                Expected to be in RGB format with values 0-255 or 0-1.
                
        Returns:
            Energy map as 2D numpy array (height, width) where higher
            values indicate more important pixels that should be preserved.
            
        Examples:
            >>> method = GradientEnergy()
            >>> energy = method(image)
            >>> assert energy.shape == image.shape[:2]
        """
        pass