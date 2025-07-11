"""
The abstract base class for energy methods in seam carving.

This module defines the `EnergyMethod` interface, which includes methods for
finding seams. It serves as a blueprint for implementing various energy
calculation strategies in seam carving algorithms.
"""

# Import standard library packages
from abc import ABC, abstractmethod
import numpy as np
# import project specific packages
from .constants import HORIZONTAL

class EnergyMethod(ABC):
    """Base class for energy methods."""
    
    image: np.ndarray
    """np.ndarray: The image data to compute energy on."""
    energy_tbl: np.ndarray
    """np.ndarray: energy table for the image."""
    energy_cst: np.ndarray
    """np.ndarray: cost table for the image."""
    seam: np.ndarray
    """np.ndarray: seam indices for the image."""
    
    def __init__(self, image):
        self.image = image
    
    @abstractmethod
    def compute_energy(self, direction: int) -> None:
        """Compute the energy map of the image."""
        raise NotImplementedError("Energy computation not implemented yet")
    
    def find_seam(self, image: np.ndarray, direction: int) -> np.ndarray:
        """Find and return a directional seam as a list of indices."""
        
        # Transpose the map if the direction is horizontal
        if direction == HORIZONTAL:
            np.transpose(image, (1, 0, 2))
        
        # Perform energy computation and cost calculation
        self.compute_energy(direction)
        self._compute_cost()
        self._compute_seam()
        
        # Retranspose the image if necessary
        if direction == HORIZONTAL:
            np.transpose(image, (1, 0, 2))
            
        # Return the computed seam
        return self.seam
    
    def _compute_cost(self) -> None:
        """Compute the cost of the energy map."""
        
        # Initialize the energy cost table with the energy table
        self.energy_cst = self.energy_tbl
        
        # Iterate through each row of the energy cost table
        for i in range(1, self.image.shape[0]):
            # Set the previous cost row
            prev = self.energy_cst[i-1]
            # Set the left and right neighbors
            left = np.roll(prev, 1)
            right = np.roll(prev, -1)
            # Set edge values to infinity
            left[0] = np.inf
            right[-1] = np.inf
            
            # Compute the minimum cost for each pixel
            self.energy_cst[i] += np.minimum.reduce([prev, left, right])
    
    def _compute_seam(self) -> None:
        """Find the minimum seam in the energy cost table."""
        
        # Intialize the seam array
        self.seam = np.zeros(self.image.shape[0], dtype=np.uint16)
        
        # Set the last index of the seam to the minimum
        self.seam[-1] = np.argmin(self.energy_cst[-1])
        
        # Backtrack to find the seam path
        for i in range(self.image.shape[0] - 2, -1, -1):
            left_bound = max(0, self.seam[i+1] - 1)
            right_bound = min(self.image.shape[1], self.seam[i+1] + 2)
            
            # Get the current row's cost
            loc = np.argmin(self.energy_cst[i, left_bound:right_bound])
            self.seam[i] = loc + left_bound

# Dynamically link the docstring of the abstract method to the class
EnergyMethod.__init__.__doc__ = EnergyMethod.__doc__