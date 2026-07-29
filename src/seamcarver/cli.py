"""
A command-line interface for the seam carving image processing tool.

This module provides a command-line interface for the seam carving tool,
allowing users to resize images, remove seams, and save seam previews.
"""

# Import standard library packages
import argparse as ap
import logging
from pathlib import Path
from time import perf_counter
from typing import Sequence

from PIL import Image

# Import project-specific packages
from ._image import normalize_image
from ._plan import DEFAULT_HIGHLIGHT_COLOR
from ._validation import validate_num_seams
from .core import plan, resize
from .logger import setup_cli_logging
from .methods import EnergyMethod, GradientEnergy, LaplacianEnergy, SobelEnergy

_ENERGY_METHODS: dict[str, type[EnergyMethod]] = {
    "gradient": GradientEnergy,
    "sobel": SobelEnergy,
    "laplacian": LaplacianEnergy,
}


def main(argv: Sequence[str] | None = None) -> None:
    # Create argument parsers for different command options
    save_parser = ap.ArgumentParser(add_help=False)
    save_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output path. A descriptive name is used when omitted.",
    )

    energy_parser = ap.ArgumentParser(add_help=False)
    energy_parser.add_argument(
        "--energy",
        choices=_ENERGY_METHODS,
        default="gradient",
        help="Energy method used to rank pixels.",
    )

    direction_parser = ap.ArgumentParser(add_help=False)
    direction_parser.add_argument(
        "-d",
        "--direction",
        choices=["vertical", "horizontal"],
        default="vertical",
        metavar="DIR",
        type=str,
        help="Direction of seams to process (vertical or horizontal).",
    )
    direction_parser.add_argument(
        "-c", "--count", type=int, default=1, help="Number of seams to process."
    )

    # Create the main argument parser
    parser = ap.ArgumentParser(
        prog="seamcarver",
        description="A command-line tool for seam carving images.",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )

    # Add global arguments
    parser.add_argument(
        "input", type=str, help="Path to the input image file for seam carving."
    )
    parser.add_argument(
        "-l",
        "--log-file",
        type=str,
        default=None,
        help="Path to save the log file.",
        metavar="LOG",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging purposes.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all output except warnings and errors.",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add the resize command
    resize_parser = subparsers.add_parser(
        "resize",
        help="Resize the image by removing seams.",
        parents=[save_parser, energy_parser],
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    resize_parser.add_argument("height", type=int, help="Output height.")
    resize_parser.add_argument("width", type=int, help="Output width.")

    # Add the remove command
    subparsers.add_parser(
        "remove",
        help="Remove seams from the image.",
        parents=[save_parser, direction_parser, energy_parser],
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )

    # Add the highlight command
    highlight_parser = subparsers.add_parser(
        "highlight",
        help="Highlight seams in the image.",
        parents=[save_parser, direction_parser, energy_parser],
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    highlight_parser.add_argument(
        "-r",
        "--rgb",
        nargs=3,
        type=int,
        default=DEFAULT_HIGHLIGHT_COLOR,
        help="Color to highlight pixels in, as a tuple in RGB format.",
        metavar=("R", "G", "B"),
    )

    # Get the command line inputs
    args = parser.parse_args(argv)

    # Set up logging based on the command line arguments
    logger = setup_cli_logging(
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file,
    )

    try:
        logger.info(f"Loading image from {args.input}...")
        image = normalize_image(args.input)
        logger.debug(f"Image loaded with shape {image.shape}.")
        output_path = _get_output_path(args)
        method = _ENERGY_METHODS[args.energy]()
        started = perf_counter()

        if args.command == "resize":
            logger.info(f"Resizing image to {args.height}x{args.width}...")
            result = resize(
                image,
                height=args.height,
                width=args.width,
                method=method,
            )
            logger.info("Image resized successfully.")

        else:
            height, width = image.shape[:2]
            if args.direction == "vertical":
                count = validate_num_seams(args.count, width)
                width -= count
            else:
                count = validate_num_seams(args.count, height)
                height -= count

            if args.command == "remove":
                logger.info(
                    f"Removing {args.count} seams in {args.direction} direction..."
                )
            else:
                logger.info(
                    f"Highlighting {args.count} seams in "
                    f"{args.direction} direction..."
                )

            resize_plan = plan(
                image,
                height=height,
                width=width,
                method=method,
            )
            if args.command == "remove":
                result = resize_plan.result()
                logger.info("Seams removed successfully.")
            else:
                result = resize_plan.preview(args.rgb)
                logger.info("Seams highlighted successfully.")

        elapsed = perf_counter() - started
        logger.info(f"Processing completed in {elapsed:.3f} seconds.")
        logger.info(f"Saving output image to {output_path}...")
        Image.fromarray(result).save(output_path)
        logger.info(f"Output image saved to {output_path}.")
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user.")
        raise SystemExit(130) from None
    except Exception as error:
        handle_error(error, logger, verbose=args.verbose)
        raise SystemExit(1) from None


def handle_error(
    error: Exception,
    logger: logging.Logger,
    verbose: bool = False,
) -> None:
    """Handle errors with logger messages."""

    if isinstance(error, FileExistsError):
        logger.error(str(error))
        logger.error("Choose another output path and try again.")
    elif isinstance(error, FileNotFoundError):
        logger.error(f"File not found: {error.filename}")
        logger.error("Please check the file path and try again.")
    elif isinstance(error, PermissionError):
        logger.error(f"Permission denied: {error.filename}")
        logger.error(
            "Please check file permissions or run the command with elevated privileges."
        )
    elif isinstance(error, ValueError):
        if "Could not load image from path" in str(error):
            logger.error("Invalid image file format.")
            logger.error("Use one of the PIL supported formats: PNG, JPEG, BMP, etc.")
        else:
            logger.error(f"Invalid input: {error}")
    elif isinstance(error, MemoryError):
        logger.error("Not enough memory to process the image.")
        logger.error("Try using a smaller image or increasing available memory.")
    else:
        logger.error("An unexpected error occurred.")
        if not verbose:
            logger.error("Use -v/--verbose for more details.")

    if verbose:
        logger.debug("Error details:", exc_info=error)


def _get_output_path(args: ap.Namespace) -> Path:
    """Return an unused explicit or derived output path."""
    if args.output is not None:
        output_path = Path(args.output)
    else:
        input_path = Path(args.input)
        suffix = input_path.suffix or ".png"
        if args.command == "resize":
            descriptor = f"resized_{args.width}x{args.height}"
        elif args.command == "remove":
            descriptor = f"removed_{args.count}_{args.direction}"
        else:
            descriptor = f"highlighted_{args.count}_{args.direction}"
        output_path = Path.cwd() / f"{input_path.stem}_{descriptor}{suffix}"

    if output_path.exists():
        raise FileExistsError(f"Output path already exists: {output_path}")
    return output_path


if __name__ == "__main__":
    main(argv=None)
