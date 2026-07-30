import logging
from io import StringIO
from types import SimpleNamespace

from seamop.cli import main
from seamop.logger import ColoredFormatter, setup_cli_logging


def test_verbose_includes_debug(capsys, input_image_path, output_path):
    main(
        [
            "resize",
            input_image_path,
            "--verbose",
            "5",
            "4",
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


def test_quiet_suppresses_info(capsys, input_image_path, output_path):
    main(
        [
            "resize",
            input_image_path,
            "--quiet",
            "5",
            "4",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert "Loading image" not in captured.err
    assert "Resizing" not in captured.err
    assert output_path.exists()


def test_file_receives_messages(capsys, input_image_path, output_path, tmp_path):
    log_path = tmp_path / "seamop.log"
    main(
        [
            "resize",
            input_image_path,
            "--log-file",
            str(log_path),
            "5",
            "4",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    contents = log_path.read_text()

    assert str(output_path) in captured.err
    assert output_path.exists()
    assert "Loading image" in contents
    assert "Processing completed in" in contents
    assert f"Output image saved to {output_path}" in contents


def test_setup_preserves_root_and_replaces_cli_handlers(tmp_path):
    root_logger = logging.getLogger()
    root_level = root_logger.level
    root_stream = StringIO()
    root_handler = logging.StreamHandler(root_stream)
    root_logger.addHandler(root_handler)

    try:
        logger = setup_cli_logging(log_file=str(tmp_path / "first.log"), color=False)
        old_handlers = logger.handlers[:]
        old_file_handler = next(
            handler
            for handler in old_handlers
            if isinstance(handler, logging.FileHandler)
        )

        logger = setup_cli_logging(color=False)
        logger.warning("CLI message")

        assert root_logger.level == root_level
        assert root_handler in root_logger.handlers
        assert root_stream.getvalue() == ""
        assert len(logger.handlers) == 1
        assert all(handler not in logger.handlers for handler in old_handlers)
        assert old_file_handler.stream is None
    finally:
        root_logger.removeHandler(root_handler)


def test_colored_formatter_does_not_mutate_record(monkeypatch):
    fake_sys = SimpleNamespace(stderr=SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr("seamop.logger.sys", fake_sys)
    record = logging.LogRecord(
        "seamop.cli", logging.ERROR, "cli.py", 1, "failure", (), None
    )

    rendered = ColoredFormatter("%(levelname)s").format(record)

    assert rendered == "\033[91mERROR\033[0m"
    assert record.levelname == "ERROR"
