"""
Unit tests for the SeamCarver class.

This module contains tests for the core functionality of the SeamCarver class,
including image resizing, seam removal, and exception handling. It ensures that
the seam carving algorithm behaves as expected when applied to sample images.

Components Tested:
- SeamCarver class:
  - Initialization and parameter handling.
  - Image resizing functionality.
  - Seam removal (vertical and horizontal).

Dependencies:
- numpy: Used to generate sample image data for testing.
- SeamCarver: The main class being tested.
- GradientEnergy: Default energy method used for testing.
- Constants (VERTICAL, HORIZONTAL): Used to specify seam directions.
"""
