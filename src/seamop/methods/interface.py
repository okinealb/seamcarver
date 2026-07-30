"""Energy-callable types and the optional class-based interface."""

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
    """Optional base class for energy-map callables.

    Examples:
        >>> import numpy as np
        >>> from seamop.methods import EnergyMethod
        >>> class CustomEnergy(EnergyMethod):
        ...     def __call__(self, image: np.ndarray) -> np.ndarray:
        ...         return image[..., 0].astype(np.float32)
        >>> image = np.zeros((2, 3, 3), dtype=np.uint8)
        >>> CustomEnergy()(image).shape
        (2, 3)
    """

    @abstractmethod
    def __call__(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.generic]:
        """Return a pixel-energy map.

        Args:
            image: RGB uint8 array shaped `(height, width, 3)`.

        Returns:
            A real numeric NumPy array matching the image height and width.
            Values must remain finite when converted to float32. Higher values
            indicate pixels that should be preserved.
        """
        pass
