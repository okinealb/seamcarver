"""
The abstract base class for energy methods in seam carving.

This module defines the `EnergyMethod` interface, which includes methods for
finding seams. It serves as a blueprint for implementing various energy
calculation strategies in seam carving algorithms.
"""

# Import standard library packages
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias

import numpy as np
import numpy.typing as npt

EnergyCallable: TypeAlias = Callable[
    [npt.NDArray[np.uint8]],
    npt.NDArray[np.generic],
]


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
    def __call__(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.generic]:
        """Compute energy map indicating pixel importance.

        Args:
            image: Input image as 3D numpy array (height, width, channels).
                Expected to be an RGB uint8 array.

        Returns:
            A real numeric NumPy array matching the image height and width.
            Values must remain finite when converted to float32. Higher values
            indicate pixels that should be preserved.

        Examples:
            >>> method = GradientEnergy()
            >>> energy = method(image)
            >>> assert energy.shape == image.shape[:2]
        """
        pass
