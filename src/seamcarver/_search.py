"""Internal single-seam dynamic-programming search."""

import numpy as np
import numpy.typing as npt


class SeamNotFoundError(Exception):
    """Raised when no finite seam remains in an energy map."""


def find_seam(
    energy: npt.NDArray[np.float32],
) -> npt.NDArray[np.bool_]:
    """Return one minimum-cost seam without modifying the energy map."""
    costs = cumulative_costs(energy)
    seam = np.zeros(energy.shape, dtype=bool)
    column = int(np.argmin(costs[-1]))

    if costs[-1, column] == np.inf:
        raise SeamNotFoundError("No valid starting point found.")

    seam[-1, column] = True
    height, width = energy.shape

    for row in range(height - 2, -1, -1):
        left = max(0, column - 1)
        right = min(width, column + 2)
        column = int(np.argmin(costs[row, left:right])) + left

        if costs[row, column] == np.inf:
            raise SeamNotFoundError("No valid seam found.")

        seam[row, column] = True

    return seam


def cumulative_costs(
    energy: npt.NDArray[np.float32],
) -> npt.NDArray[np.float64]:
    """Return cumulative minimum seam costs for an energy map."""
    costs = energy.astype(np.float64, copy=True)

    for row in range(1, energy.shape[0]):
        previous = costs[row - 1]
        current = costs[row]
        current[1:-1] += np.minimum(
            np.minimum(previous[:-2], previous[1:-1]),
            previous[2:],
        )
        current[0] += min(previous[0], previous[1])
        current[-1] += min(previous[-1], previous[-2])

    return costs
