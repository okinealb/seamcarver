import numpy as np
import pytest

from seamcarver import VERTICAL, SeamCarver

SEED = 42
IMAGE_SIZES = (512, 1024, 2048)
SEAM_COUNTS = (1, 5, 50, 200)


def _remove_vertical_seams(carver, num_seams):
    carver.remove(VERTICAL, num_seams)
    return carver.image


@pytest.mark.parametrize("size", IMAGE_SIZES, ids=lambda size: f"{size}x{size}")
@pytest.mark.parametrize(
    "num_seams",
    SEAM_COUNTS,
    ids=lambda num_seams: f"{num_seams}-seams",
)
def test_vertical_seam_removal(benchmark, size, num_seams):
    image = np.random.default_rng(SEED).integers(
        0,
        256,
        (size, size, 3),
        dtype=np.uint8,
    )

    def setup():
        return (SeamCarver(image), num_seams), {}

    benchmark.extra_info.update(
        {
            "direction": "vertical",
            "energy_method": "GradientEnergy",
            "image_size": f"{size}x{size}",
            "num_seams": num_seams,
            "seed": SEED,
        }
    )
    result = benchmark.pedantic(
        _remove_vertical_seams,
        setup=setup,
        rounds=5,
        warmup_rounds=1,
    )

    assert result.shape == (size, size - num_seams, 3)
