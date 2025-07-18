"""
Utility functions for seam carving.

Note: This class assumes that the image is always in a vertical orientation
for seam carving. For horizontal seams, the image should be transposed
before passing it to the methods.
"""

# Import standard library packages
import numpy as np

def mask(seam: np.ndarray, dims: tuple[int,int]) -> np.ndarray:
    """Create a mask of pixels to keep based on the seam indices."""
    # Initialize a mask with all pixels set to True
    mask = np.ones(dims, dtype=bool)
    rows = np.arange(len(seam))
    # Set the seam pixels to False
    mask[rows, seam] = False
    return mask