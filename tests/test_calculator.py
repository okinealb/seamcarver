"""
Unit tests for the SeamCalculator class.

This module contains tests for the core functionality of the SeamCalculator
class, including energy table, energy cost, and minimum seam computations.
It ensures that the seam carving algorithm behaves as expected when applied to
sample images.

Components Tested:
- SeamCalculator class:
  - Initialization and parameter handling.
  - Image resizing functionality.
  - Seam removal (vertical and horizontal).

Dependencies:
- numpy: Used to generate sample image data for testing.
- SeamCalculator: The main class being tested.
- GradientEnergy: Default energy method used for testing.
"""
