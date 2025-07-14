"""
Utility functions for seam carving.
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