"""
A library for seam carving images, allowing for resizing by removing seams.
This module provides the `Carver` class, which implements the seam carving
algorithm. It includes methods for loading images, resizing them by removing
vertical or horizontal seams, and displaying or saving the modified images.

For more information on seam carving, refer to the
[Wikipedia article](https://en.wikipedia.org/wiki/Seam_carving).
"""

# Import general packages
from PIL import Image
import numpy as np
# Import project specific packages
from .calculator import SeamCalculator
from .constants import VERTICAL, HORIZONTAL
from .methods import EnergyMethod, GradientEnergy
# Import utility functions
from . import utils

# Main class for seam carving operations
class SeamCarver:
    """A class to implement the seam carving algorithm for image resizing.
    
    Attributes:
        image (np.ndarray): Image data as a numpy array.
        shape (tuple[int, int, int]): Dimensions of the image as (rows, cols).
        verbose (bool): Flag for verbose output.
        calculator (SeamCalculator): Instance for calculating seams.
        
    Note: This class supports both vertical and horizontal seam carving by 
    transposing the image as needed. Thus, all downstream methods and modules
    assume that the image orientated for vertical seam carving (column removal).
    """

    # Class attributes
    image: np.ndarray
    """np.ndarray: image data as a numpy array."""
    shape: tuple[int, int, int]
    """tuple[int, int, int]: dimensions of image as (rows, cols, channels)."""
    verbose: bool
    """bool: flag for verbose output."""
    calculator: SeamCalculator
    """SeamCalculator: instance for calculating seams."""

    def __init__(
        self,
        image: np.ndarray | list[list[int]] | Image.Image | str,
        method: EnergyMethod = GradientEnergy(),
        verbose: bool = False
    ):
        """Initialize the SeamCarver with an image and configuration.
    
        Args:
            image: Input image in various supported formats:
                - np.ndarray: Direct numpy array (height, width, channels)
                - list[list[int]]: Doubly nested list of pixel values
                - Image.Image: PIL Image object
                - str: Path to image file
            method: Energy calculation method for seam detection.
                Defaults to GradientEnergy().
            verbose: Enable verbose output during operations.
                Defaults to False.
        
        Raises:
            FileNotFoundError: If image file path is invalid.
            ValueError: If image format is unsupported.
            TypeError: If image type is invalid.
            MemoryError: If insufficient memory to load image.
        
        Examples:
            >>> carver = SeamCarver("path/to/image.jpg")
            >>> carver = SeamCarver(image_array, method=SobelEnergy())
            >>> carver = SeamCarver(pil_image, verbose=True)
        """
        
        # Check for exceptions during initialization
        try:
            if isinstance(image, np.ndarray):
                self.image = image
            elif isinstance(image, list):
                self.image = np.array(image, dtype=np.uint8)
            elif isinstance(image, Image.Image):
                self.image = np.array(image.convert("RGB"), dtype=np.uint8)
            elif isinstance(image, str):
                with Image.open(image) as img:
                    self.image = np.array(img.convert("RGB"), dtype=np.uint8)
            else:
                raise ValueError(
                    "Invalid image input. Must be one of np.ndarray, list, "
                    + "Image.Image, or str."
                )

            # Initialize other parameters
            self.shape = self.image.shape
            self.verbose = verbose
            self.calculator = SeamCalculator(self.image, method)

        # Handle errors initializing the SeamCarver
        except FileNotFoundError as e:
            raise ValueError(f"Could not load image from path: {image}") from e

    def resize(self, height: int, width: int) -> None:
        """Resize the image to the specified height and width."""
        # Remove seams until the image reaches the desired dimensions
        self.remove(num_seams=self.shape[1] - width, direction=VERTICAL)
        self.remove(num_seams=self.shape[0] - height, direction=HORIZONTAL)

    def remove(self, num_seams: int = 1, direction: int = VERTICAL) -> None:
        """Remove the minimum seam from the image."""
    
        # Transpose the image if the direction is horizontal
        is_horizontal = direction == HORIZONTAL
        if is_horizontal:
            self.image = np.transpose(self.image, (1, 0, 2))
    
        for _ in range(num_seams):
            seam = self.calculator.find_seam(self.image)
            bool_mask = utils.mask(seam, (self.image.shape[0], self.image.shape[1]))
            # Remove the seam from the image by exclusion
            self.image = self.image[bool_mask].reshape(
                self.image.shape[0], self.image.shape[1] - 1, 3
            )

        # Retranspose the image if the direction is horizontal
        if is_horizontal:
            self.image = np.transpose(self.image, (1, 0, 2))

    def highlight(self, direction: int = VERTICAL) -> None:
        """Highlight the minimum seam in the image."""
        # Transpose the image if the direction is horizontal
        is_horizontal = direction == HORIZONTAL
        if is_horizontal:
            self.image = np.transpose(self.image, (1, 0, 2))
        
        seam = self.calculator.find_seam(self.image)
        bool_mask = utils.mask(seam, (self.image.shape[0], self.image.shape[1]))
        # Highlight the seam in red
        self.image[~bool_mask] = np.array([255, 0, 0])
        
        # Retranspose the image if the direction is horizontal
        if is_horizontal:
            self.image = np.transpose(self.image, (1, 0, 2))

    def save(self, output_path: str = 'output.jpg') -> None:
        """Save the carved image to the specified path."""    
        Image.fromarray(self.image).save(output_path)
        
    def display(self) -> None:
        """Display the current state of the image."""
        Image.fromarray(self.image).show()

# Example usage of the SeamCarver class
if __name__ == "__main__":
    example = SeamCarver("examples/sample.jpg")
    example.display()
    example.resize(example.shape[0] - 2, example.shape[1] - 2)
    example.display()