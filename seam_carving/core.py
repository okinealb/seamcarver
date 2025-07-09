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
from .interfaces import EnergyMethod
from .methods import SobelEnergy

# Constants for seam direction to be used internally
VERTICAL: int = 0
"""int: Indicates a vertical seam direction (top to bottom)."""

HORIZONTAL: int = 1
"""int: Indicates a horizontal seam direction (left to right)."""

# Main class for seam carving operations
class SeamCarver:
    """A class to implement the seam carving algorithm for image resizing."""

    def __init__(self, image_path: str, method: EnergyMethod = NotImplemented):
        """Load the image and initialize other parameters"""
        
        # Setup object attributes
        self.image: Image.Image = Image.open(image_path).convert("RGB")
        self.rows, self.cols = self.image.size
        self.method: EnergyMethod = method if method else SobelEnergy()
        
        raise NotImplementedError("SeamCarver method not implemented yet")

    def resize(self, height: int, width: int) -> None:
        """Resize the image to the specified height and width"""
        raise NotImplementedError("SeamCarver method not implemented yet")

    def remove(self, num_seams: int = 1, direction: int = VERTICAL) -> None:
        """Remove the minimum seam from the image"""
        raise NotImplementedError("SeamCarver method not implemented yet")
  
    def highlight(self, num_seams: int = 1, direction: int = VERTICAL) -> None:
        """Highlight the minimum seam in the image"""
        raise NotImplementedError("SeamCarver method not implemented yet")
  
    def save(self, output_path: str = 'output.jpg') -> None:
        """Save the carved image to the specified path"""
        raise NotImplementedError("SeamCarver method not implemented yet")

    def display(self) -> None:
        """Display the current state of the image"""
        raise NotImplementedError("SeamCarver method not implemented yet")
    
# Example usage of the SeamCarver class
if __name__ == "__main__":
    example = SeamCarver("examples/sample.jpg")
    example.display()
    example.resize(example.rows - 2, example.cols - 2)
    example.display()