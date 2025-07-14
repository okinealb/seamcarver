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
from .methods.interface import EnergyMethod
from .methods import GradientEnergy
# Import utility functions
from .utils.utils import mask
from .utils.logger import setup_logging

# Main class for seam carving operations
class SeamCarver:
    """A class to implement the seam carving algorithm for image resizing.
    
    Attributes:
        image (np.ndarray): Image data as a numpy array.
        shape (tuple[int, int, int]): Dimensions of the image as (rows, cols).
        method (EnergyMethod): Method to calculate the energy of the image.
        verbose (bool): Flag for verbose output.
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
        image: np.ndarray | list[int] | Image.Image | str,
        method: EnergyMethod = GradientEnergy(),
        verbose: bool = False
    ):
        """Load the image and initialize other parameters."""
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
                raise ValueError("Invalid image input. Must be one of np.ndarray, list, Image.Image, str.")
            
            # Initialize other parameters
            self.shape = self.image.shape
            self.verbose = verbose
            self.calculator = SeamCalculator(self.image, method)
            self.calculator.image = self.image
            
                
        # Handle errors initializing the SeamCarver
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image}")
        except ValueError:
            raise ValueError("Invalid image format.")
        except TypeError:
            raise TypeError("Invalid image type.")
        except MemoryError:
            raise MemoryError("Not enough memory to load the image.")
        except Exception as e:
            raise ValueError(f"Error initializing SeamCarver: {e}")

    def resize(self, height: int, width: int) -> None:
        """Resize the image to the specified height and width."""
        # Remove seams until the image reaches the desired dimensions
        self.remove(num_seams=self.shape[1] - width, direction=VERTICAL)
        self.remove(num_seams=self.shape[0] - height, direction=HORIZONTAL)
        # Update the dimensions after resizing
        #self.shape = height, width, 3

    def remove(self, num_seams: int = 1, direction: int = VERTICAL) -> None:
        """Remove the minimum seam from the image."""
    
        # Transpose the image if the direction is horizontal
        is_horizontal = direction == HORIZONTAL
        if is_horizontal:
            self.image = np.transpose(self.image, (1, 0, 2))
    
        for _ in range(num_seams):
            seam = self.calculator.find_seam(self.image)
            bool_mask = mask(seam, (self.image.shape[0], self.image.shape[1]))
            # Remove the seam from the image
            self.image = self.image[bool_mask].reshape(
                self.image.shape[0], self.image.shape[1] - 1, 3
            )
                
        # Retranspose the image if the direction is horizontal
        if is_horizontal:
            self.image = np.transpose(self.image, (1, 0, 2))

    def highlight(self, direction: int = VERTICAL) -> None:
        """Highlight the minimum seam in the image."""
        seam = self.calculator.find_seam()
        bool_mask = mask(seam, (self.shape[0], self.shape[1]))
        # Highlight the seam in red
        self.image[~bool_mask] = np.array([255, 0, 0])

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