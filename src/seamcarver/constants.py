"""
Constants for the seam carving package.

This module defines direction constants and default values used throughout
the seamcarver library. Direction constants follow NumPy axis conventions
where 0 is horizontal and 1 is vertical.
"""

# Constants for seam direction to be used internally
HORIZONTAL: int = 0
"""int: Indicates horizontal seam orientation (left to right)."""
VERTICAL: int = 1
"""int: Indicates vertical seam orientation (top to bottom)."""
BORDER_ENERGY: int = 1000
"""int: Default energy value for border pixels in the energy map."""
HIGHLIGHT_COLOR: list[int] = [255, 0, 0]
"""list[int]: Default color used to highlight seams in the image (red in RGB)."""