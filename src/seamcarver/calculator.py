"""Advanced vertical seam calculation."""

from typing import SupportsIndex

import numpy as np
import numpy.typing as npt

from ._image import _validate_ndarray
from ._planner import find_seams
from ._validation import validate_num_seams
from .methods import GradientEnergy
from .methods.interface import EnergyCallable


class SeamCalculator:
    """Find vertical seams with a configurable energy callable.

    Attributes:
        method: Callable that computes pixel energy for seam detection.

    Examples:
        >>> import numpy as np
        >>> from seamcarver.calculator import SeamCalculator
        >>> image = np.zeros((4, 5, 3), dtype=np.uint8)
        >>> calculator = SeamCalculator()
        >>> seam_mask = calculator(image, num_seams=2)
        >>> seam_mask.shape, int(seam_mask.sum())
        ((4, 5), 8)

    Note:
        This advanced interface calculates vertical seams. The top-level API
        handles image normalization and horizontal resizing.
    """

    method: EnergyCallable
    """Callable used to calculate image energy."""

    def __init__(self, method: EnergyCallable = GradientEnergy()) -> None:
        """Set the energy callable used for seam selection.

        Args:
            method: Callable returning an energy map. Defaults to
                :class:`GradientEnergy`.
        """
        self.method = method

    def __call__(
        self,
        image: npt.NDArray[np.uint8],
        num_seams: SupportsIndex,
    ) -> npt.NDArray[np.bool_]:
        """Return vertical seams as a source-sized boolean mask.

        The source array is not mutated.

        Args:
            image: RGB uint8 NumPy array shaped (height, width, 3).
            num_seams: Number of seams to find. Must be at least one and less
                than the image width.

        Returns:
            A `(height, width)` mask whose true values identify seam pixels.
        """

        _validate_ndarray(image)
        num_seams = validate_num_seams(num_seams, image.shape[1])
        return find_seams(
            image,
            num_seams,
            self._compute_energy,
        )

    def _compute_energy(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Compute energy map using configured energy method."""
        energy = self.method(image)
        if not isinstance(energy, np.ndarray):
            raise TypeError("Energy method must return a NumPy array.")
        if energy.shape != image.shape[:2]:
            raise ValueError(
                f"Energy map must have shape {image.shape[:2]}; got {energy.shape}."
            )
        if not (
            np.issubdtype(energy.dtype, np.integer)
            or np.issubdtype(energy.dtype, np.floating)
        ):
            raise TypeError("Energy map must contain real numeric values.")

        with np.errstate(over="ignore", invalid="ignore"):
            normalized_energy = np.array(energy, dtype=np.float32, copy=True)
        if not np.isfinite(normalized_energy).all():
            raise ValueError("Energy map must contain only finite float32 values.")
        return normalized_energy
