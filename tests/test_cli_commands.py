import numpy as np
import pytest
from PIL import Image

from seamcarver.cli import main


def test_resize_writes_requested_dimensions(capsys, input_image_path, output_path):
    main(
        [
            input_image_path,
            "resize",
            "4",
            "5",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert "Loading image" in captured.err
    assert "Resizing" in captured.err
    assert "Saving" in captured.err
    assert str(output_path) in captured.err
    with Image.open(output_path) as output:
        assert output.size == (5, 4)


def test_resize_without_output_does_not_save(
    capsys, input_image_path, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    main([input_image_path, "resize", "4", "5"])

    captured = capsys.readouterr()

    assert "Resizing" in captured.err
    assert "Saving" not in captured.err
    assert not (tmp_path / "output.jpg").exists()


@pytest.mark.parametrize(
    ("direction", "count", "size"),
    [
        ("vertical", "2", (5, 6)),
        ("horizontal", "2", (7, 4)),
    ],
    ids=["vertical", "horizontal"],
)
def test_remove_writes_expected_dimensions(
    direction, count, size, capsys, input_image_path, output_path
):
    main(
        [
            input_image_path,
            "remove",
            "--direction",
            direction,
            "--count",
            count,
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert "Removing" in captured.err
    assert direction in captured.err
    assert str(output_path) in captured.err
    with Image.open(output_path) as output:
        assert output.size == size


def test_remove_defaults_to_one_seam(capsys, input_image_path, output_path):
    main(
        [
            input_image_path,
            "remove",
            "--direction",
            "vertical",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert "Removing" in captured.err
    assert str(output_path) in captured.err
    with Image.open(output_path) as output:
        assert output.size == (6, 6)


@pytest.mark.parametrize(
    ("direction", "count", "expected_pixels"),
    [
        ("vertical", "2", 12),
        ("horizontal", None, 7),
    ],
    ids=["vertical-count", "horizontal-default"],
)
def test_highlight_writes_colored_seams(
    direction,
    count,
    expected_pixels,
    capsys,
    input_image_path,
    output_path,
    monkeypatch,
):
    monkeypatch.setattr("PIL.Image.Image.show", lambda self: None)
    args = [
        input_image_path,
        "highlight",
        "--direction",
        direction,
        "--output",
        str(output_path),
    ]
    if count is not None:
        args.extend(["--count", count])

    main(args)

    captured = capsys.readouterr()

    assert "Highlighting" in captured.err
    assert direction in captured.err
    with Image.open(output_path) as output:
        pixels = np.asarray(output)
        assert output.size == (7, 6)
        assert np.all(pixels == (255, 0, 0), axis=-1).sum() == expected_pixels
