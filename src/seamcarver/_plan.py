"""Internal resize-plan result and construction."""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from .calculator import SeamCalculator
from .constants import HIGHLIGHT_COLOR


@dataclass(eq=False, frozen=True, slots=True)
class _ResizePlan:
    """Store one completed resize and its source-pixel removals."""

    _source: npt.NDArray[np.uint8]
    _result: npt.NDArray[np.uint8]
    _removed: npt.NDArray[np.bool_]

    def __post_init__(self) -> None:
        self._source.flags.writeable = False
        self._result.flags.writeable = False
        self._removed.flags.writeable = False

    @property
    def source_shape(self) -> tuple[int, int, int]:
        return (
            self._source.shape[0],
            self._source.shape[1],
            self._source.shape[2],
        )

    @property
    def target_shape(self) -> tuple[int, int, int]:
        return (
            self._result.shape[0],
            self._result.shape[1],
            self._result.shape[2],
        )

    def carve(self) -> npt.NDArray[np.uint8]:
        """Return an owned copy of the planned result."""
        return self._result.copy()

    def highlight(
        self,
        color: Sequence[int] = HIGHLIGHT_COLOR,
    ) -> npt.NDArray[np.uint8]:
        """Return an owned source image with planned removals colored."""
        preview = self._source.copy()
        preview[self._removed] = color
        return preview


def build_plan(
    image: npt.NDArray[np.uint8],
    *,
    height: int,
    width: int,
    calculator: SeamCalculator,
) -> _ResizePlan:
    """Build a width-first shrinking plan from validated inputs."""
    source = image.copy()
    working = image.copy()
    source_height, source_width = image.shape[:2]
    source_indices: npt.NDArray[np.signedinteger] = np.arange(
        source_height * source_width
    ).reshape(source_height, source_width)
    removed = np.zeros(source_height * source_width, dtype=bool)

    if width < source_width:
        working, source_indices, removed_indices = _remove(
            working,
            source_indices,
            source_width - width,
            calculator,
        )
        removed[removed_indices] = True

    if height < source_height:
        oriented_image = np.transpose(working, (1, 0, 2))
        oriented_indices = source_indices.T
        oriented_image, oriented_indices, removed_indices = _remove(
            oriented_image,
            oriented_indices,
            source_height - height,
            calculator,
        )
        removed[removed_indices] = True
        working = np.ascontiguousarray(np.transpose(oriented_image, (1, 0, 2)))

    return _ResizePlan(
        source,
        working,
        removed.reshape(source_height, source_width),
    )


def _remove(
    image: npt.NDArray[np.uint8],
    source_indices: npt.NDArray[np.signedinteger],
    num_seams: int,
    calculator: SeamCalculator,
) -> tuple[
    npt.NDArray[np.uint8],
    npt.NDArray[np.signedinteger],
    npt.NDArray[np.signedinteger],
]:
    """Remove planned seams from an oriented image and its source map."""
    mask = calculator(image, num_seams)
    height = image.shape[0]
    return (
        image[~mask].reshape(height, -1, 3),
        source_indices[~mask].reshape(height, -1),
        source_indices[mask],
    )
