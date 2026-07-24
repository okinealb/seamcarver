from seamcarver.cli import main


def test_verbose_includes_debug(capsys, cli_image_path, output_path):
    main(
        [
            cli_image_path,
            "--verbose",
            "resize",
            "4",
            "5",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert "Loading image" in captured.err
    assert "DEBUG:" in captured.err
    assert "Image loaded with shape" in captured.err
    assert str(output_path) in captured.err
    assert output_path.exists()


def test_quiet_suppresses_info(capsys, cli_image_path, output_path):
    main(
        [
            cli_image_path,
            "--quiet",
            "resize",
            "4",
            "5",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert "Loading image" not in captured.err
    assert "Resizing" not in captured.err
    assert output_path.exists()


def test_file_receives_messages(capsys, cli_image_path, output_path, tmp_path):
    log_path = tmp_path / "seamcarver.log"
    main(
        [
            cli_image_path,
            "--log-file",
            str(log_path),
            "resize",
            "4",
            "5",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    contents = log_path.read_text()

    assert str(output_path) in captured.err
    assert output_path.exists()
    assert "Loading image" in contents
    assert "Output image saved successfully" in contents
