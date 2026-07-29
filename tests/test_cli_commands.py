import numpy as np
import pytest
from PIL import Image

from seamcarver.cli import main
from seamcarver.methods import GradientEnergy, LaplacianEnergy, SobelEnergy


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
    assert "Processing completed in" in captured.err
    with Image.open(output_path) as output:
        assert output.size == (5, 4)


def test_resize_without_output_uses_descriptive_name(
    capsys, input_image_path, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    main([input_image_path, "resize", "4", "5"])

    captured = capsys.readouterr()
    default_output = tmp_path / "input_resized_5x4.png"

    assert "Resizing" in captured.err
    assert str(default_output) in captured.err
    with Image.open(default_output) as output:
        assert output.size == (5, 4)


@pytest.mark.parametrize(
    ("command", "filename"),
    [
        (["remove", "--count", "2"], "input_removed_2_vertical.png"),
        (["highlight", "--count", "2"], "input_highlighted_2_vertical.png"),
    ],
    ids=["remove", "highlight"],
)
def test_command_without_output_uses_descriptive_name(
    command, filename, input_image_path, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "PIL.Image.Image.show",
        lambda self: pytest.fail("CLI attempted to display an image"),
    )

    main([input_image_path, *command])

    assert (tmp_path / filename).exists()


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
    monkeypatch.setattr(
        "PIL.Image.Image.show",
        lambda self: pytest.fail("CLI attempted to display an image"),
    )
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


@pytest.mark.parametrize(
    ("option", "energy_type"),
    [
        (None, GradientEnergy),
        ("gradient", GradientEnergy),
        ("sobel", SobelEnergy),
        ("laplacian", LaplacianEnergy),
    ],
    ids=["default", "gradient", "sobel", "laplacian"],
)
def test_resize_selects_energy_method(
    option,
    energy_type,
    input_image_path,
    output_path,
    monkeypatch,
):
    selected_method = None

    def fake_resize(image, *, height, width, method):
        nonlocal selected_method
        selected_method = method
        return image[:height, :width]

    monkeypatch.setattr("seamcarver.cli.resize", fake_resize)
    args = [input_image_path, "resize", "4", "5", "--output", str(output_path)]
    if option is not None:
        args.extend(["--energy", option])

    main(args)

    assert isinstance(selected_method, energy_type)
