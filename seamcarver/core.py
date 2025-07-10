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
from .constants import VERTICAL, HORIZONTAL
from .interfaces import EnergyMethod
from .methods import SobelEnergy
from . import utils

# Main class for seam carving operations
class SeamCarver:
    """A class to implement the seam carving algorithm for image resizing."""

    def __init__(
        self,
        image_path: str,
        method: EnergyMethod = SobelEnergy(),
        verbose: bool = False
    ):
        """Load the image and initialize other parameters."""
        # Check for exceptions during initialization
        try:
            # Initialize the object with the image and other parameters
            with Image.open(image_path) as img:
                self.image = np.array(img.convert("RGB"))
                """np.ndarray: image data as a numpy array."""
                self.rows, self.cols = self.image.shape[:2]
                """int: rows (height) and cols (width) of the image."""
                self.method = method
                """EnergyMethod: method to calculate the energy of the image."""
                self.verbose = verbose
                """bool: flag for verbose output."""
                
        # Handle file not found and other exceptions
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise ValueError(f"Error initializing SeamCarver: {e}")

    def resize(self, height: int, width: int) -> None:
        """Resize the image to the specified height and width."""
        # Remove seams until the image reaches the desired dimensions
        self.remove(num_seams=self.cols - width, direction=VERTICAL)
        self.remove(num_seams=self.rows - height, direction=HORIZONTAL)
        # Update the dimensions after resizing
        self.rows, self.cols = height, width

    def remove(self, num_seams: int = 1, direction: int = VERTICAL) -> None:
        """Remove the minimum seam from the image."""
        for _ in range(num_seams):
            seam = self.method.find_seam(self.image, direction)
            mask = utils.mask(seam, (self.rows, self.cols), direction)
            # Apply the mask and reshape the image accordingly
            if direction == VERTICAL:
                self.image = self.image[mask].reshape(self.rows, self.cols - 1, 3)
            elif direction == HORIZONTAL:
                self.image = self.image[mask].reshape(self.rows - 1, self.cols, 3)
            else:
                raise ValueError("Invalid direction specified. Use VERTICAL or HORIZONTAL.")
  
    def highlight(self, direction: int = VERTICAL) -> None:
        """Highlight the minimum seam in the image."""
        seam = self.method.find_seam(self.image, direction)
        mask = utils.mask(seam, (self.rows, self.cols), direction)
        # Highlight the seam in red
        self.image[~mask] = np.array([255, 0, 0])

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
    example.resize(example.rows - 2, example.cols - 2)
    example.display()