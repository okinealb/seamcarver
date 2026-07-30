import pytest

from seamop.cli import main


def test_missing_image_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["resize", "nonexistent.jpg", "5", "4"])

    captured = capsys.readouterr()

    assert captured.err
    assert exc_info.value.code != 0


def test_invalid_image_reports_supported_formats(capsys, tmp_path):
    input_path = tmp_path / "invalid.png"
    output_path = tmp_path / "output.png"
    input_path.write_text("not an image")

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "resize",
                str(input_path),
                "5",
                "4",
                "--output",
                str(output_path),
            ]
        )

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "Invalid image file format." in captured.err
    assert "PIL supported formats" in captured.err
    assert "Invalid input:" not in captured.err
    assert not output_path.exists()


@pytest.mark.parametrize(
    "command",
    [
        ["resize", "0", "5"],
        ["remove", "--count", "0"],
        ["highlight", "0", "5"],
    ],
    ids=["resize", "remove", "highlight"],
)
def test_processing_error_does_not_save(command, capsys, input_image_path, output_path):
    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                command[0],
                input_image_path,
                *command[1:],
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

    monkeypatch.setattr("seamop.cli.resize", fail_resize)

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "resize",
                input_image_path,
                "5",
                "4",
                "--output",
                str(output_path),
            ]
        )

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "Output path already exists" in captured.err
    assert output_path.read_bytes() == original


def test_existing_default_output_is_not_overwritten(
    capsys, input_image_path, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    output_path = tmp_path / "input_resized_5x4.png"
    original = b"existing output"
    output_path.write_bytes(original)

    def fail_resize(*args, **kwargs):
        pytest.fail("Resize started before output validation")

    monkeypatch.setattr("seamop.cli.resize", fail_resize)

    with pytest.raises(SystemExit) as exc_info:
        main(["resize", input_image_path, "5", "4"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert str(output_path) in captured.err
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

    monkeypatch.setattr("seamop.cli.resize", fail_resize)
    args = ["resize", input_image_path]
    if verbose:
        args.append("--verbose")
    args.extend(["5", "4"])

    with pytest.raises(SystemExit) as exc_info:
        main(args)

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "An unexpected error occurred." in captured.err
    assert ("Traceback" in captured.err) is shows_traceback


def test_keyboard_interrupt_exits_130(capsys, input_image_path, monkeypatch):
    def interrupt_resize(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr("seamop.cli.resize", interrupt_resize)

    with pytest.raises(SystemExit) as exc_info:
        main(["resize", input_image_path, "5", "4"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 130
    assert "Operation cancelled by user." in captured.err


def test_usage_error_is_concise(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["resize", "input.png", "bad", "5"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "Error: Invalid value for WIDTH" in captured.err
    assert "Try 'seamop resize --help'" in captured.err
    assert "Usage:" not in captured.err
    assert "Traceback" not in captured.err


def test_help_lists_commands_and_aliases(capsys):
    main(["--help"])
    main(["remove", "--help"])
    main(["highlight", "--help"])

    captured = capsys.readouterr()

    assert captured.out.index("resize") < captured.out.index("remove")
    assert captured.out.index("remove") < captured.out.index("highlight")
    for long, short in (
        ("--help", "-h"),
        ("--direction", "-d"),
        ("--count", "-c"),
        ("--rgb", "-r"),
        ("--output", "-o"),
        ("--energy", "-e"),
        ("--log-file", "-l"),
        ("--verbose", "-v"),
        ("--quiet", "-q"),
    ):
        assert any(
            option in captured.out
            for option in (
                f"{long}, {short}",
                f"{long} ({short})",
                f"{long} {short}",
                f"{short}  {long}",
                f"{short} {long}",
            )
        )

    output_line = next(line for line in captured.out.splitlines() if "--output" in line)
    energy_line = next(line for line in captured.out.splitlines() if "--energy" in line)
    assert output_line.index("-o") < output_line.index("--output")
    assert output_line.index("--output") == energy_line.index("--energy")
