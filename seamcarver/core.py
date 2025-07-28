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
# Import project-specific packages
from .calculator import SeamCalculator
from .constants import VERTICAL, HORIZONTAL, HIGHLIGHT_COLOR
from .methods import EnergyMethod, GradientEnergy


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
        verbose: bool = False,
    ):
        """Initialize the SeamCarver with an image and configuration.
    
        Args:
            image: Input image in various supported formats:
                - np.ndarray: Direct numpy array (height, width, channels)
                - list[list[int]]: Doubly nested list of pixel values
                - Image.Image: PIL Image object
                - str: Path to image file
            method (EnergyMethod): Energy calculation method for seam detection.
                Defaults to GradientEnergy().
            verbose (bool): Enable verbose output during operations.
                Defaults to False.
        
        Raises:
            FileNotFoundError: If image file path is invalid.
            ValueError: If image format is unsupported.
            TypeError: If image type is invalid.
            MemoryError: If insufficient memory to load image.
        
        Examples:
            >>> from seamcarver import SeamCarver, SobelEnergy
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
                    "Image.Image, or str."
                )

            # Initialize other parameters
            self.shape = self.image.shape
            self.verbose = verbose
            self.calculator = SeamCalculator(method)

        # Handle errors initializing the SeamCarver
        except FileNotFoundError as e:
            raise ValueError(f"Could not load image from path: {image}") from e


    def resize(
        self, 
        height: int, 
        width: int,
    ) -> None:
        """Resize the image to the specified height and width."""
        
        # Remove seams until the image reaches the desired dimensions
        self.remove(direction=VERTICAL, num_seams=self.shape[1] - width)
        self.remove(direction=HORIZONTAL, num_seams=self.shape[0] - height)


    def remove(
        self, 
        direction: int, 
        num_seams: int,
    ) -> None:
        """Remove the minimum seam(s) from the image."""
    
        # Transpose the image if the direction is horizontal
        if direction == HORIZONTAL:
            self.image = np.transpose(self.image, (1, 0, 2))
    
        # Calculate the seam mask using the calculator
        mask = self.calculator(self.image, num_seams)
        # Remove the seam from the image by exclusion
        self.image = self.image[~mask].reshape(
            self.image.shape[0], -1, 3
        )

        # Re-transpose the image if the direction is horizontal
        if direction == HORIZONTAL:
            self.image = np.transpose(self.image, (1, 0, 2))
    

    def highlight(self, 
        direction: int = VERTICAL, 
        num_seams: int = 1,
        color: list[int] = HIGHLIGHT_COLOR,
    ) -> None:
        """Highlight the minimum seam(s) in the image."""
        
        # Transpose the image if the direction is horizontal
        if direction == HORIZONTAL:
            self.image = np.transpose(self.image, (1, 0, 2))
        
        mask = self.calculator(self.image, num_seams)
        self.image[mask] = color
        
        # Re-transpose the image if the direction is horizontal
        if direction == HORIZONTAL:
            self.image = np.transpose(self.image, (1, 0, 2))
            

    def display(self) -> None:
        """Display the current state of the image."""
        Image.fromarray(self.image).show()
        
        
    def save(self, output_path: str = 'output.jpg') -> None:
        """Save the carved image to the specified path."""    
        Image.fromarray(self.image).save(output_path)
        

# Example usage of the SeamCarver class
if __name__ == "__main__":
    example = SeamCarver("examples/sample.jpg")
    example.display()
    example.resize(example.shape[0] - 2, example.shape[1] - 2)
    example.display()