"""Internal multi-seam planning."""

from collections.abc import Callable

import numpy as np
import numpy.typing as npt

from ._search import SeamNotFoundError, find_seam

EnergyComputer = Callable[
    [npt.NDArray[np.uint8]],
    npt.NDArray[np.float32],
]


def find_seams(
    image: npt.NDArray[np.uint8],
    num_seams: int,
    compute_energy: EnergyComputer,
    batch_size: int = 1,
) -> npt.NDArray[np.bool_]:
    """Return planned seams in the source image's coordinates."""
    height, width = image.shape[:2]
    image = image.copy()
    kept: npt.NDArray[np.signedinteger] = np.arange(height * width)

    while num_seams > 0:
        found, seams = _find_batch(
            image,
            num_seams,
            batch_size,
            compute_energy,
        )
        if found == 0:
            raise RuntimeError("Seam extraction made no progress.")

        num_seams -= found
        image = image[~seams].reshape(height, -1, 3)
        kept = kept[~seams.ravel()]

    mask = np.ones(height * width, dtype=bool)
    mask[kept] = False
    return mask.reshape(height, width)


def _find_batch(
    image: npt.NDArray[np.uint8],
    num_seams: int,
    batch_size: int,
    compute_energy: EnergyComputer,
) -> tuple[int, npt.NDArray[np.bool_]]:
    """Find one batch of nonoverlapping seams."""
    seams = np.zeros(image.shape[:2], dtype=bool)
    energy = compute_energy(image)
    found = 0

    while found < min(batch_size, num_seams):
        try:
            seam = find_seam(energy)
        except SeamNotFoundError:
            break

        seams = seams | seam
        energy[seam] = np.inf
        found += 1

    return found, seams
