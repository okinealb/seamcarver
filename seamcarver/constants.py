"""
The constants used throughout the seam carving package.

These constants are used internally to indicate the direction of seams. They
are defined here for clarity and consistency across the package. Note, that 
these directions correspond to the usage of `axis` in NumPy functions, where
`0` is horizontal (left to right) and `1` is vertical (top to bottom).
"""

# Constants for seam direction to be used internally
HORIZONTAL: int = 0
"""int: Indicates a horizontal seam direction (left to right)."""
VERTICAL: int = 1
"""int: Indicates a vertical seam direction (top to bottom)."""