"""
Unit tests for the CLI functionality of the seamcarver package.

This module tests the command-line interface (CLI) of the seamcarver package,
ensuring that commands like `resize` and `remove` work as expected. It
validates the handling of command-line arguments, logging behavior, and output
to stdout/stderr.

Components Tested:
- CLI commands:
  - `resize`: Resizes an image to specified dimensions.
  - `remove`: Removes a number of seams from an image.
  - `highlight`: Highlights a number of seams in an image.

Dependencies:
- pytest: Used for capturing stdout/stderr during CLI tests.
- seamcarver.cli: The main CLI entry point being tested.
"""