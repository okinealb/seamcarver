"""
A command-line interface for the seam carving image processing tool.

This module provides a command-line interface for the seam carving tool,
allowing users to highlight, remove, and display seams in images.
It also supports an interactive mode for easier use.
"""

# Import standard library packages
import argparse
import sys
# Import project specific packages
from .core import SeamCarver
from .constants import VERTICAL, HORIZONTAL

def main():
    # Create the main argument parser
    parser = argparse.ArgumentParser(
        prog='seamcarver',
        description="A command-line tool for seam carving images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Add global arguments
    parser.add_argument('image', type=str, default='examples/sample.jpg',
        help='Path to the input image file for seam carving.')
    parser.add_argument('-o', '--output', type=str, default='output.jpg',
        help='Path to save the output image after seam carving.',)
    parser.add_argument('--log-file', type=str, default=None,
        help='Path to save the log file. If not specified, logs will be printed to stderr.',)
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Enable verbose output for debugging purposes.',)
    parser.add_argument('-q', '--quiet', action='store_true',
        help='Suppress all output except warnings and errors.',)
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Add the resize command
    resize_parser = subparsers.add_parser('resize',
        help='Resize the image by removing seams.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    resize_parser.add_argument('height', type=int, help='Output height.')
    resize_parser.add_argument('width', type=int, help='Output width.')
    
    # Add the remove command
    remove_parser = subparsers.add_parser('remove',
        help='Remove seams from the image.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    remove_parser.add_argument('direction', choices=['vertical', 'horizontal'],
        help='Direction of seams to remove (vertical or horizontal).')
    remove_parser.add_argument('count', type=int, default=1,
        help='Number of seams to remove.')
    
    # Add the highlight command
    highlight_parser = subparsers.add_parser('highlight',
        help='Highlight seams in the image.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    highlight_parser.add_argument('direction', choices=['vertical', 'horizontal'],
        help='Direction of seams to highlight (vertical or horizontal).')
    highlight_parser.add_argument('count', type=int, default=1,
        help='Number of seams to highlight.')
    
    # Get the command line inputs
    args = parser.parse_args()

    try:
        # Initialize the SeamCarver with the provided image
        carver = SeamCarver(args.image, verbose=args.verbose)
    except Exception as e:
        sys.exit(1)

    if args.command == 'resize':
        carver.resize(height=args.height, width=args.width)
        try:
            carver.save(output_path=args.output)
        except Exception as e:
            sys.exit(1)
        
    elif args.command == 'remove':
        # Set the seam direction based on the command
        direction = VERTICAL if args.direction == 'vertical' else HORIZONTAL
        carver.remove(num_seams=args.count, direction=direction)
        try:
            carver.save(output_path=args.output)
        except Exception as e:
            sys.exit(1)
        
    elif args.command == 'highlight':
        # Set the seam direction based on the command
        direction = VERTICAL if args.direction == 'vertical' else HORIZONTAL
        carver.highlight(direction=direction)
        carver.display()
    
if __name__ == "__main__":
    main()