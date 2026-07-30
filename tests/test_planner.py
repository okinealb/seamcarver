import numpy as np
import pytest

from seamop._planner import find_seams


def test_tracks_source_coordinates_across_batches():
    image = np.zeros((2, 100, 3), dtype=np.uint8)
    original = image.copy()
    widths = []

    def column_energy(current):
        widths.append(current.shape[1])
        columns = np.arange(current.shape[1], dtype=np.float32)
        return np.broadcast_to(columns, current.shape[:2]).copy()

    mask = find_seams(image, 10, column_energy, batch_size=4)

    assert widths == [100, 96, 92]
    assert np.array_equal(np.flatnonzero(mask[0]), np.arange(10))
    assert np.all(mask.sum(axis=1) == 10)
    assert np.array_equal(image, original)


def test_stops_without_progress(monkeypatch):
    image = np.zeros((2, 3, 3), dtype=np.uint8)
    no_seams = np.zeros(image.shape[:2], dtype=bool)
    monkeypatch.setattr(
        "seamop._planner._find_batch",
        lambda image, num_seams, batch_size, compute_energy: (0, no_seams),
    )

    with pytest.raises(RuntimeError, match="no progress"):
        find_seams(
            image,
            1,
            lambda current: np.zeros(current.shape[:2], dtype=np.float32),
        )
