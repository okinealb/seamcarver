"""
Core seam detection module for content-aware image resizing.

This module provides the `SeamCalculator` class, which implements the
seam carving algorithm using dynamic programming. It includes methods
for finding optimal seams through images based on energy computation.

For more information on seam carving, refer to the
[Wikipedia article](https://en.wikipedia.org/wiki/Seam_carving).
"""

from typing import SupportsIndex

import numpy as np
import numpy.typing as npt

from ._planner import find_seams
from ._validation import validate_num_seams
from .methods import GradientEnergy
from .methods.interface import EnergyCallable


# Main class for seam carving calculations
class SeamCalculator:
    """Calculator for seam carving operations using dynamic programming.

    This class implements the core seam carving algorithm to find optimal
    seams (connected paths) through an image based on energy computation. The
    calculator uses dynamic programming to efficiently find minimum energy
    paths suitable for image resizing.

    Attributes:
        method: Callable that computes pixel energy for seam detection.

    Examples:
        >>> calculator = SeamCalculator()
        >>> seam_mask = calculator(image, num_seams=5)

        >>> from seamcarver import SobelEnergy
        >>> calculator = SeamCalculator(method=SobelEnergy())
        >>> seam_mask = calculator(image, num_seams=10)

    Note:
        This class assumes vertical seam orientation. For horizontal seams,
        transpose the image before passing to the calculator.
    """

    # Class attributes
    method: EnergyCallable
    """Callable used to calculate image energy."""

    def __init__(self, method: EnergyCallable = GradientEnergy()) -> None:
        """Initialize the SeamCalculator with an energy computation method.

        Args:
            method: Method for computing pixel energy values.
                Defaults to GradientEnergy().
        """
        self.method = method

    def __call__(
        self,
        image: npt.NDArray[np.uint8],
        num_seams: SupportsIndex,
    ) -> npt.NDArray[np.bool_]:
        """Find optimal seams in image and return as boolean mask.

        Seams are removed from an internal image copy, and retained pixel indices
        are tracked via a flattened map. This allows reconstruction of all seam
        positions without mutating the caller's image.

        Args:
            image: Input image as numpy array (height, width, channels).
            num_seams: Number of seams to find. Must be at least one and less
                than the image width.

        Returns:
            mask: (height, width) where True indicates seam pixels.

        Examples:
            >>> mask = calculator(image, 1)
            >>> assert mask.sum() == image.shape[0]  # One pixel per row
        """

        num_seams = validate_num_seams(num_seams, image.shape[1])
        return find_seams(
            image,
            num_seams,
            self._compute_energy,
        )

    def mask_to_index(
        self, mask: npt.NDArray[np.bool_]
    ) -> npt.NDArray[np.signedinteger]:
        """Convert boolean seam mask to flat array of linear indices.

        Args:
            mask: Boolean mask where True indicates seam pixels.

        Returns:
            1D array of indices for seam pixels.
        """
        return np.flatnonzero(mask)

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
