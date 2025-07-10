"""
Utility functions for seam carving.
"""

# Import standard library packages
import numpy as np
# Import project specific packages
from .constants import VERTICAL, HORIZONTAL

def mask(seam: np.ndarray, dims: tuple[int,int], direction: int = VERTICAL) -> np.ndarray:
    """Create a mask of pixels to keep based on the seam indices."""
    # Initialize a mask with all pixels set to True
    mask = np.ones(dims, dtype=bool)
    rows = np.arange(len(seam))
    # Set the seam pixels to False based on the direction
    if direction == VERTICAL:
        mask[rows, seam] = False
    elif direction == HORIZONTAL:
        mask[seam, rows] = False
    return mask