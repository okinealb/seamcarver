from pathlib import Path

import numpy as np
import pytest

from seamcarver import ResizePlan, plan, resize


class TestResize:
    def test_returns_owned_image_without_mutating_input(self):
        image = np.arange(4 * 5 * 3, dtype=np.uint8).reshape(4, 5, 3)
        original = image.copy()

        result = resize(image, height=3, width=3)

        assert result.shape == (3, 3, 3)
        assert result.dtype == np.uint8
        assert result.flags.owndata
        assert not np.shares_memory(result, image)
        assert np.array_equal(image, original)

    def test_matches_planned_result(self):
        image = np.arange(4 * 5 * 3, dtype=np.uint8).reshape(4, 5, 3)

        result = resize(image, height=3, width=3)
        resize_plan = plan(image, height=3, width=3)

        assert np.array_equal(result, resize_plan.carve())

    def test_same_size_returns_independent_image(self):
        image = np.zeros((2, 3, 3), dtype=np.uint8)

        result = resize(image, height=2, width=3)

        assert np.array_equal(result, image)
        assert not np.shares_memory(result, image)

    def test_accepts_pathlike_input(self, input_image_path):
        result = resize(Path(input_image_path), height=4, width=5)

        assert result.shape == (4, 5, 3)

    def test_targets_are_keyword_only(self):
        image = np.zeros((2, 3, 3), dtype=np.uint8)

        with pytest.raises(TypeError):
            resize(image, 2, 2)


class TestPlan:
    def test_reuses_computed_seams(self):
        image = np.zeros((3, 4, 3), dtype=np.uint8)
        calls = 0

        def left_edge_energy(current):
            nonlocal calls
            calls += 1
            columns = np.arange(current.shape[1], dtype=np.float32)
            return np.broadcast_to(columns, current.shape[:2]).copy()

        resize_plan = plan(image, height=3, width=2, method=left_edge_energy)
        first_result = resize_plan.carve()
        second_result = resize_plan.carve()
        first_preview = resize_plan.highlight()
        second_preview = resize_plan.highlight()

        assert isinstance(resize_plan, ResizePlan)
        assert repr(resize_plan) == (
            "ResizePlan(source_shape=(3, 4, 3), target_shape=(3, 2, 3))"
        )
        assert resize_plan.source_shape == (3, 4, 3)
        assert resize_plan.target_shape == (3, 2, 3)
        assert calls == 2
        assert np.array_equal(first_result, second_result)
        assert np.array_equal(first_preview, second_preview)
        assert not np.shares_memory(first_result, second_result)
        assert not np.shares_memory(first_preview, second_preview)

    @pytest.mark.parametrize(
        ("color", "exception"),
        [
            ((1, 2), ValueError),
            ((1, 2, 3, 4), ValueError),
            ((-1, 2, 3), ValueError),
            ((1, 2, 256), ValueError),
            ((1, 2, 3.0), TypeError),
            ((1, 2, True), TypeError),
        ],
        ids=[
            "two-channels",
            "four-channels",
            "negative",
            "over-255",
            "float",
            "boolean",
        ],
    )
    def test_highlight_rejects_invalid_color(self, color, exception):
        resize_plan = plan(
            np.zeros((2, 3, 3), dtype=np.uint8),
            height=2,
            width=2,
        )

        with pytest.raises(exception):
            resize_plan.highlight(color)
