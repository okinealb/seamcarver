from itertools import product

import numpy as np
import pytest

from seamop._search import SeamNotFoundError, cumulative_costs, find_seam


def minimum_seam_cost(energy):
    """Return the cheapest connected top-to-bottom path."""
    height, width = energy.shape
    paths = product(range(width), repeat=height)
    return min(
        sum(energy[row, column] for row, column in enumerate(path))
        for path in paths
        if all(abs(left - right) <= 1 for left, right in zip(path, path[1:]))
    )


@pytest.mark.parametrize(
    "energy",
    [
        np.array([[4, 1, 3]], dtype=np.float32),
        np.array([[3, 1], [1, 3]], dtype=np.float32),
        np.array(
            [
                [5, 1, 4, 3],
                [2, 6, 1, 7],
                [4, 2, 3, 1],
            ],
            dtype=np.float32,
        ),
    ],
    ids=["single-row", "two-rows", "three-rows"],
)
def test_finds_minimum_connected_seam_without_mutation(energy):
    original = energy.copy()

    mask = find_seam(energy)
    columns = np.argmax(mask, axis=1)

    assert mask.shape == energy.shape
    assert mask.dtype == np.bool_
    assert np.all(mask.sum(axis=1) == 1)
    assert np.all(np.abs(np.diff(columns)) <= 1)
    assert energy[mask].sum() == minimum_seam_cost(energy)
    assert np.array_equal(energy, original)


@pytest.mark.parametrize("sign", [-1, 1], ids=["negative", "positive"])
def test_cumulative_costs_remain_finite(sign):
    energy = np.full(
        (3, 3),
        sign * np.finfo(np.float32).max,
        dtype=np.float32,
    )

    costs = cumulative_costs(energy)

    assert costs.dtype == np.float64
    assert np.isfinite(costs).all()


def test_rejects_exhausted_energy():
    energy = np.full((3, 3), np.inf, dtype=np.float32)

    with pytest.raises(SeamNotFoundError):
        find_seam(energy)
