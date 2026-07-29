"""Public operations for content-aware image resizing."""

from typing import SupportsIndex

import numpy as np
import numpy.typing as npt

from ._image import ImageInput, normalize_image
from ._plan import ResizePlan, build_plan
from ._validation import validate_resize_target
from .calculator import SeamCalculator
from .methods import GradientEnergy
from .methods.interface import EnergyCallable


def plan(
    image: ImageInput,
    *,
    height: SupportsIndex,
    width: SupportsIndex,
    method: EnergyCallable = GradientEnergy(),
) -> ResizePlan:
    """Compute a reusable width-first resize plan.

    Args:
        image: Supported image input converted to an owned RGB uint8 array.
        height: Positive target height no larger than the source height.
        width: Positive target width no larger than the source width.
        method: Callable that computes an energy map for an RGB uint8 array.

    Returns:
        A plan that can render the carved result or highlight removed pixels
        without repeating seam search.
    """
    normalized = normalize_image(image)
    height = validate_resize_target("height", height, normalized.shape[0])
    width = validate_resize_target("width", width, normalized.shape[1])
    return build_plan(
        normalized,
        height=height,
        width=width,
        calculator=SeamCalculator(method),
    )


def resize(
    image: ImageInput,
    *,
    height: SupportsIndex,
    width: SupportsIndex,
    method: EnergyCallable = GradientEnergy(),
) -> npt.NDArray[np.uint8]:
    """Return an owned RGB uint8 image resized width-first.

    The source input is not mutated. Target dimensions must be positive and no
    larger than the source because seam addition is not implemented.
    """
    return plan(
        image,
        height=height,
        width=width,
        method=method,
    ).result()
