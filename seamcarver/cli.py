"""
A command-line interface for the seam carving image processing tool.

This module provides a command-line interface for the seam carving tool,
allowing users to highlight, remove, and display seams in images.
It also supports an interactive mode for easier use.
"""

# Import standard library packages
import argparse as ap
import logging
import sys
from typing import Sequence
# Import project-specific packages
from .core import SeamCarver
from .constants import VERTICAL, HORIZONTAL, HIGHLIGHT_COLOR
from .logger import setup_cli_logging, get_logger


def main(argv: Sequence[str] | None = None) -> None:
    # Create argument parsers for different command options
    save_parser = ap.ArgumentParser(add_help=False)
    save_parser.add_argument('-o', '--output', type=str, default='output.jpg',
        help='Path to save the output image after seam carving.')
    
    direction_parser = ap.ArgumentParser(add_help=False)
    direction_parser.add_argument('-d', '--direction',
        choices=['vertical', 'horizontal'],
        default='vertical', metavar='DIR', type=str,
        help='Direction of seams to process (vertical or horizontal).')
    direction_parser.add_argument('-c', '--count', type=int, default=1,
        help='Number of seams to process.')
    
    # Create the main argument parser
    parser = ap.ArgumentParser(
        prog='seamcarver',
        description="A command-line tool for seam carving images.",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    
    # Add global arguments
    parser.add_argument('input', type=str,
        help='Path to the input image file for seam carving.')
    parser.add_argument('-l', '--log-file', type=str, default=None,
        help='Path to save the log file.',
        metavar='LOG')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Enable verbose output for debugging purposes.',)
    parser.add_argument('-q', '--quiet', action='store_true',
        help='Suppress all output except warnings and errors.',)
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Add the resize command
    resize_parser = subparsers.add_parser('resize',
        help='Resize the image by removing seams.',
        parents=[save_parser],
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    resize_parser.add_argument('height', type=int, help='Output height.')
    resize_parser.add_argument('width', type=int, help='Output width.')
    
    # Add the remove command
    remove_parser = subparsers.add_parser('remove',
        help='Remove seams from the image.',
        parents=[save_parser, direction_parser],
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    
    # Add the highlight command
    highlight_parser = subparsers.add_parser('highlight',
        help='Highlight seams in the image.',
        parents=[save_parser, direction_parser],
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    highlight_parser.add_argument('-r', '--rgb', nargs=3, type=int,
        default=HIGHLIGHT_COLOR,
        help='Color to highlight pixels in, as a tuple in RGB format.',
        metavar=('R','G','B'))
    
    # Get the command line inputs
    args = parser.parse_args(argv)
    
    # Set up logging based on the command line arguments, then get the logger
    setup_cli_logging(
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file,
    )
    logger = get_logger(__name__)

    # Initialize the SeamCarver with the provided image
    try:
        logger.info(f"Loading image from {args.input}...")
        carver = SeamCarver(args.input, verbose=args.verbose)
        logger.debug(f"Image loaded with shape {carver.shape}.")
    except Exception as e:
        handle_error(e, logger, verbose=args.verbose)
        sys.exit(1)

    if args.command == 'resize':
        logger.info(f"Resizing image to {args.height}x{args.width}...")
        carver.resize(height=args.height, width=args.width)
        logger.info("Image resized successfully.")
        logger.info(f"Saving output image to {args.output}...")

    elif args.command == 'remove':
        direction = VERTICAL if args.direction == 'vertical' else HORIZONTAL

        logger.info(f"Removing {args.count} seams in {args.direction} direction...")
        carver.remove(direction=direction, num_seams=args.count)
        logger.info("Seams removed successfully.")
        logger.info(f"Saving output image to {args.output}...")
        
    elif args.command == 'highlight':
        direction = VERTICAL if args.direction == 'vertical' else HORIZONTAL

        logger.info(f"Highlighting {args.count} seams in {args.direction} direction...")
        carver.highlight(direction=direction, num_seams=args.count, color=args.rgb)
        logger.info("Seams highlighted successfully.")
        logger.debug(f"Displaying highlighted image...")
        carver.display()
        logger.debug("Image display completed.")
        
    try:
        carver.save(output_path=args.output)
        logger.info("Output image saved successfully.")
    except Exception as e:
        handle_error(e, logger, verbose=args.verbose)
        sys.exit(1)
    
def handle_error(
    error: Exception,
    logger: logging.Logger,
    verbose: bool = False,
) -> None:
    """Handle errors with logger messages."""
    
    if isinstance(error, FileNotFoundError):
        logger.error(f"File not found: {error.filename}")
        logger.error("Please check the file path and try again.")
    elif isinstance(error, PermissionError):
        logger.error(f"Permission denied: {error.filename}")
        logger.error("Please check file permissions or run the command with elevated privileges.")
    elif isinstance(error, ValueError):
        if "Could not load image from path" in str(error):
            logger.error("Invalid image file format.")
            logger.error("Use one of the PIL supported formats: PNG, JPEG, BMP, etc.")
        else:
            logger.error(f"Invalid input: {error}")
    elif isinstance(error, MemoryError):
        logger.error("Not enough memory to process the image.")
        logger.error("Try using a smaller image or increasing available memory.")
    elif isinstance(error, KeyboardInterrupt):
        logger.warning("Operation cancelled by user.")
    else:
        logger.error("An unexpected error occurred.")
        if verbose:
            logger.debug(f"Error details: {error}")
        else: 
            logger.error("Use -v/--verbose for more details.")
    
if __name__ == "__main__":
    main(argv=None)