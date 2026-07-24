"""
A library for seam carving images, allowing for resizing by removing seams.
This module provides the `Carver` class, which implements the seam carving
algorithm. It includes methods for loading images, resizing them by removing
vertical or horizontal seams, and displaying or saving the modified images.

For more information on seam carving, refer to the
[Wikipedia article](https://en.wikipedia.org/wiki/Seam_carving).
"""

from typing import SupportsIndex

import numpy as np

# Import general packages
from PIL import Image

# Import project-specific packages
from ._image import ImageInput, normalize_image
from ._validation import validate_direction, validate_resize_target
from .calculator import SeamCalculator
from .constants import HIGHLIGHT_COLOR, HORIZONTAL, VERTICAL
from .methods import EnergyMethod, GradientEnergy


def _orient_image(image: np.ndarray, direction: int) -> np.ndarray:
    """Return an image oriented for vertical seam processing."""
    if direction == HORIZONTAL:
        return np.transpose(image, (1, 0, 2))
    return image


# Main class for seam carving operations
class SeamCarver:
    """
    A class to implement the seam carving algorithm for image resizing.

    Attributes:
        image (np.ndarray): Image data as a numpy array.
        shape (tuple[int, int, int]): Dimensions of the image as (rows, cols).
        verbose (bool): Flag for verbose output.
        calculator (SeamCalculator): Instance for calculating seams.

    Note:
        This class supports both vertical and horizontal seam carving by
        transposing the image as needed. Thus, all downstream methods and
        modules assume that the image is oriented for vertical seam carving
        (column removal).
    """

    # Class attributes
    image: np.ndarray
    """np.ndarray: image data as a numpy array."""
    verbose: bool
    """bool: flag for verbose output."""
    calculator: SeamCalculator
    """SeamCalculator: instance for calculating seams."""

    def __init__(
        self,
        image: ImageInput,
        method: EnergyMethod = GradientEnergy(),
        verbose: bool = False,
    ):
        """Initialize the SeamCarver with an image and configuration.

        Args:
            image: Input image in various supported formats:
                - np.ndarray: RGB uint8 array shaped (height, width, 3)
                - list: Rectangular RGB integer data with values from 0 to 255
                - Image.Image: PIL image converted to RGB
                - str or os.PathLike: Path to an image converted to RGB
            method (EnergyMethod): Energy calculation method for seam detection.
                Defaults to GradientEnergy().
            verbose (bool): Enable verbose output during operations.
                Defaults to False.

        Raises:
            FileNotFoundError: If an image path does not exist.
            ValueError: If image contents, dimensions, channels, or dtype are invalid.
            TypeError: If the image type is unsupported.
            MemoryError: If insufficient memory to load image.

        Examples:
            >>> from seamcarver import SeamCarver, SobelEnergy
            >>> carver = SeamCarver("path/to/image.jpg")
            >>> carver = SeamCarver(image_array, method=SobelEnergy())
            >>> carver = SeamCarver(pil_image, verbose=True)
        """

        self.image = normalize_image(image)
        self.verbose = verbose
        self.calculator = SeamCalculator(method)

    @property
    def shape(self) -> tuple[int, int, int]:
        """tuple[int, int, int]: dimensions of image as (rows, cols, channels)."""
        return self.image.shape

    def resize(
        self,
        height: SupportsIndex,
        width: SupportsIndex,
    ) -> None:
        """Shrink the image to positive dimensions no larger than its current size.

        The image is restored if either directional removal fails.
        """
        height = validate_resize_target("height", height, self.shape[0])
        width = validate_resize_target("width", width, self.shape[1])
        original_image = self.image

        try:
            if width < self.shape[1]:
                self.remove(direction=VERTICAL, num_seams=self.shape[1] - width)
            if height < self.shape[0]:
                self.remove(direction=HORIZONTAL, num_seams=self.shape[0] - height)
        except BaseException:
            # Restore state even when resizing is interrupted
            self.image = original_image
            raise

    def remove(
        self,
        direction: SupportsIndex,
        num_seams: SupportsIndex,
    ) -> None:
        """Remove one or more seams in a supported direction."""
        direction = validate_direction(direction)
        oriented_image = _orient_image(self.image, direction)
        mask = self.calculator(oriented_image, num_seams)
        carved_image = oriented_image[~mask].reshape(oriented_image.shape[0], -1, 3)
        self.image = _orient_image(carved_image, direction)

    def add(
        self,
        direction: SupportsIndex,
        num_seams: SupportsIndex,
    ) -> None:
        """Report that seam addition is not implemented."""
        raise NotImplementedError("Seam addition is not implemented.")

    def highlight(
        self,
        direction: SupportsIndex = VERTICAL,
        num_seams: SupportsIndex = 1,
        color: list[int] = HIGHLIGHT_COLOR,
    ) -> None:
        """Highlight one or more seams in a supported direction."""
        direction = validate_direction(direction)
        oriented_image = _orient_image(self.image, direction)
        mask = self.calculator(oriented_image, num_seams)
        oriented_image[mask] = color

    def display(self) -> None:
        """Display the current state of the image."""
        Image.fromarray(self.image).show()

    def save(self, output_path: str = "output.jpg") -> None:
        """Save the carved image to the specified path."""
        Image.fromarray(self.image).save(output_path)


# Example usage of the SeamCarver class
if __name__ == "__main__":
    example = SeamCarver("examples/sample.jpg")
    example.display()
    example.resize(example.shape[0] - 2, example.shape[1] - 2)
    example.display()
