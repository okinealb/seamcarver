import pytest

from seamcarver.cli import main


def test_missing_image_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["nonexistent.jpg", "resize", "4", "5"])

    captured = capsys.readouterr()

    assert captured.err
    assert exc_info.value.code != 0


@pytest.mark.parametrize(
    "command",
    [
        ["resize", "0", "5"],
        ["remove", "--count", "0"],
        ["highlight", "--count", "0"],
    ],
    ids=["resize", "remove", "highlight"],
)
def test_processing_error_does_not_save(command, capsys, input_image_path, output_path):
    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                input_image_path,
                *command,
                "--output",
                str(output_path),
            ]
        )

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "Invalid input:" in captured.err
    assert "Traceback" not in captured.err
    assert not output_path.exists()


def test_existing_output_is_not_overwritten(
    capsys, input_image_path, output_path, monkeypatch
):
    original = b"existing output"
    output_path.write_bytes(original)

    def fail_resize(*args, **kwargs):
        pytest.fail("Resize started before output validation")

    monkeypatch.setattr("seamcarver.cli.resize", fail_resize)

    with pytest.raises(SystemExit) as exc_info:
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

    assert exc_info.value.code == 1
    assert "Output path already exists" in captured.err
    assert output_path.read_bytes() == original


@pytest.mark.parametrize(
    ("verbose", "shows_traceback"),
    [(False, False), (True, True)],
    ids=["default", "verbose"],
)
def test_unexpected_error_controls_traceback(
    verbose, shows_traceback, capsys, input_image_path, monkeypatch
):
    def fail_resize(*args, **kwargs):
        raise RuntimeError("resize failed")

    monkeypatch.setattr("seamcarver.cli.resize", fail_resize)
    args = [input_image_path]
    if verbose:
        args.append("--verbose")
    args.extend(["resize", "4", "5"])

    with pytest.raises(SystemExit) as exc_info:
        main(args)

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "An unexpected error occurred." in captured.err
    assert ("Traceback" in captured.err) is shows_traceback


def test_keyboard_interrupt_exits_130(capsys, input_image_path, monkeypatch):
    def interrupt_resize(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr("seamcarver.cli.resize", interrupt_resize)

    with pytest.raises(SystemExit) as exc_info:
        main([input_image_path, "resize", "4", "5"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 130
    assert "Operation cancelled by user." in captured.err
