"""Internal validation for seam-operation parameters."""

import operator
from typing import SupportsIndex

import numpy as np

from .constants import HORIZONTAL, VERTICAL


def _as_index(value: SupportsIndex, name: str) -> int:
    """Return a lossless integer value while rejecting booleans."""
    if isinstance(value, (bool, np.bool_)):
        raise TypeError(f"{name} must be an integer, not a boolean.")
    try:
        return operator.index(value)
    except TypeError as error:
        raise TypeError(f"{name} must be an integer.") from error


def validate_direction(direction: SupportsIndex) -> int:
    """Return a supported seam direction."""
    direction = _as_index(direction, "direction")
    if direction not in (HORIZONTAL, VERTICAL):
        raise ValueError(
            f"direction must be HORIZONTAL ({HORIZONTAL}) or VERTICAL ({VERTICAL})."
        )
    return direction


def validate_num_seams(num_seams: SupportsIndex, width: int) -> int:
    """Return a valid seam count for the current image width."""
    num_seams = _as_index(num_seams, "num_seams")
    if num_seams < 1:
        raise ValueError("num_seams must be greater than zero.")
    if num_seams >= width:
        raise ValueError(f"num_seams must be less than the image width of {width}.")
    return num_seams


def validate_resize_target(
    name: str,
    value: SupportsIndex,
    current: int,
) -> int:
    """Return a shrinking or unchanged resize target."""
    target = _as_index(value, name)
    if target < 1:
        raise ValueError(f"{name} must be greater than zero.")
    if target > current:
        raise ValueError(
            f"{name} cannot exceed the current {name} of {current}; "
            "seam addition is not implemented."
        )
    return target
