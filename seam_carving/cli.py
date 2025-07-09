"""
A command-line interface for the seam carving image processing tool.

This module provides a command-line interface for the seam carving tool,
allowing users to highlight, remove, and display seams in images.
It also supports an interactive mode for easier use.
"""

import argparse
from seam_carving import SeamCarver

def main():
    # Create the main argument parser
    parser = argparse.ArgumentParser(
        prog='seam_carving',
        description="A command-line tool for seam carving images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Add the image argument
    parser.add_argument('image', type=str, default='examples/sample.jpg',
        help='Path to the input image file for seam carving.')
    
    # Add the output argument
    parser.add_argument('-o', '--output', type=str, default=None,
        help='Path to save the output image after seam carving.',
        required=False)
    # Add the verbose argument
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Enable verbose output for debugging purposes.',
        required=False)
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Add the resize command
    resize_parser = subparsers.add_parser('resize',
        help='Resize the image by removing seams.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    resize_parser.add_argument('width', type=int, help='Output width.')
    resize_parser.add_argument('height', type=int, help='Output height.')
    
    # Add the interactive command
    interactive_parser = subparsers.add_parser('interactive',
        help='Enable interactive mode for seam carving.',)
    
    # Get the command line inputs
    args = parser.parse_args()
    
    pass
    
if __name__ == "__main__":
    main()