import numpy as np
import pytest
from PIL import Image

from seamcarver._image import normalize_image


class TestArrayInput:
    def test_preserves_shape_and_dtype(self, sample_image):
        normalized = normalize_image(sample_image)

        assert normalized.shape == sample_image.shape
        assert normalized.dtype == np.uint8
        assert isinstance(normalized, np.ndarray)

    def test_is_copied(self, sample_image):
        normalized = normalize_image(sample_image)

        sample_image[0, 0] = [1, 2, 3]

        assert not np.array_equal(normalized[0, 0], sample_image[0, 0])

    @pytest.mark.parametrize(
        "image",
        [
            np.zeros((3, 3), dtype=np.uint8),
            np.zeros((3, 3, 4), dtype=np.uint8),
            np.zeros((0, 3, 3), dtype=np.uint8),
            np.zeros((3, 0, 3), dtype=np.uint8),
            np.zeros((3, 3, 3), dtype=np.int64),
            np.zeros((3, 3, 3), dtype=np.float32),
        ],
        ids=[
            "two-dimensional",
            "rgba",
            "zero-height",
            "zero-width",
            "int64",
            "float32",
        ],
    )
    def test_rejects_invalid_values(self, image):
        with pytest.raises(ValueError):
            normalize_image(image)


class TestListInput:
    def test_becomes_rgb_uint8(self, sample_image):
        normalized = normalize_image(sample_image.tolist())

        assert normalized.shape == sample_image.shape
        assert normalized.dtype == np.uint8

    @pytest.mark.parametrize(
        "image",
        [
            [[[0, 0, 0], [0, 0]]],
            [[[-1, 0, 0]]],
            [[[256, 0, 0]]],
            [[[0.0, 0.0, 0.0]]],
            [],
        ],
        ids=["ragged", "negative", "over-byte", "float", "empty"],
    )
    def test_rejects_invalid_values(self, image):
        with pytest.raises(ValueError):
            normalize_image(image)


@pytest.mark.parametrize("mode", ["L", "RGBA"])
def test_pil_input_becomes_rgb_uint8(mode):
    normalized = normalize_image(Image.new(mode, (3, 2)))

    assert normalized.shape == (2, 3, 3)
    assert normalized.dtype == np.uint8


class TestPathInput:
    @pytest.mark.parametrize(
        "use_path_object", [False, True], ids=["string", "path-object"]
    )
    def test_loads_rgb_uint8(self, sample_image, tmp_path, use_path_object):
        image_path = tmp_path / "test_image.png"
        Image.fromarray(sample_image).save(image_path)
        image_input = image_path if use_path_object else str(image_path)

        normalized = normalize_image(image_input)

        assert normalized.shape == sample_image.shape
        assert normalized.dtype == np.uint8

    def test_missing_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            normalize_image(str(tmp_path / "missing.png"))

    def test_undecodable_raises_value_error(self, tmp_path):
        image_path = tmp_path / "invalid.png"
        image_path.write_bytes(b"not an image")

        with pytest.raises(ValueError, match="Could not decode image"):
            normalize_image(str(image_path))


def test_unsupported_input_raises_type_error():
    with pytest.raises(TypeError):
        normalize_image(object())
