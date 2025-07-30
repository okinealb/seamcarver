"""
Core seam detection module for content-aware image resizing.

This module provides the `SeamCalculator` class, which implements the
seam carving algorithm using dynamic programming. It includes methods
for finding optimal seams through images based on energy computation.

For more information on seam carving, refer to the
[Wikipedia article](https://en.wikipedia.org/wiki/Seam_carving).
"""

# Import standard library packages
import numpy as np
# import project specific packages
from .methods import EnergyMethod, GradientEnergy


class SeamCalculator:
    """Calculator for seam carving operations using dynamic programming.
    
    This class implements the core seam carving algorithm to find optimal
    seams (connected paths) through an image based on energy computation. The
    calculator uses dynamic programming to efficiently find minimum energy
    paths suitable for image resizing.
    
    Attributes:
        method (EnergyMethod): Energy computation method for detecting image
            features and edges.
    
    Examples:
        >>> calculator = SeamCalculator()
        >>> seam_mask = calculator(image, num_seams=5)
        
        >>> from seamcarver import SobelEnergy
        >>> calculator = SeamCalculator(method=SobelEnergy())
        >>> seam_mask = calculator(image, num_seams=10)
        
    Note:
        This class assumes vertical seam orientation. For horizontal seams,
        transpose the image before passing to the calculator.
    """

    # Class constants
    MAP_DIMS_TO_SIZE: list[tuple[int, int]] = [ # (width, percentage)
        (1000, 8),  # 12.5% per batch for images >= 1000 pixels
        (500, 10),  # 10.0% per batch for images >= 500 pixels
        (100, 12),  # ~8.3% per batch for images >= 100 pixels
        (20, 15),   # ~6.7% per batch for images >= 0 pixels
        (0, 20),    #  5.0% per batch for images < 20 pixels
    ]
    """list[tuple[int, int]]: Rules for batch size based on image dimensions.
        Each tuple contains (minimum dimension, batch size)."""

    # Class attributes
    method: EnergyMethod
    """EnergyMethod: method to calculate the energy of the image."""


    def __init__(self, method: EnergyMethod = GradientEnergy()):
        """Initialize the SeamCalculator with an energy computation method.
        
        Args:
            method: Method for computing pixel energy values. 
                Defaults to GradientEnergy().
        """
        self.method = method


    def __call__(
        self,
        image: np.ndarray,
        num_seams: int,
    ) -> np.ndarray:
        """Find optimal seams in image and return as boolean mask.
        
        Uses dynamic programming to find the specified number of minimum
        energy seams. For multiple seams, employs intelligent batching 
        to prevent seam clustering.
        
        Args:
            image: Input image as numpy array (height, width, channels).
            num_seams: Number of seams to find. Must be positive.
                
        Returns:
            mask: (height, width) where True indicates seam pixels.

        Examples:
            >>> mask = calculator(image, 1)
            >>> assert mask.sum() == image.shape[0]  # One pixel per row
        """
        
        # If only one seam is requested, compute it directly
        if num_seams == 1:
            energy = self._compute_energy(image)
            costs = self._compute_costs(energy)
            seams = self._compute_seams(energy, costs)
            return seams
        
        # Otherwise, process in batches
        else:
            # Determine the batch size based on the image width
            batch_size = self._get_batch_size(image.shape[1])
            
            # Initialize the seams mask with the image shape
            seams = np.zeros(image.shape[:2], dtype=bool)
            # Compute energy once
            energy = self._compute_energy(image)
            
            while num_seams > 0:
                for _ in range(min(batch_size, num_seams)):
                    # Compute costs and seams for the current batch
                    costs_i = self._compute_costs(energy)
                    seams_i = self._compute_seams(energy, costs_i)
                    seams = seams | seams_i # binary OR to accumulate seams
                
                num_seams -= batch_size # Update the number of seams left
            
            return seams # return the final seams mask


    def mask_to_index(self, mask: np.ndarray) -> np.ndarray:
        """Convert boolean seam mask to flat array of linear indices.
        
        Args:
            mask: Boolean mask where True indicates seam pixels.
                
        Returns:
            1D array of indices for seam pixels.
        """
        # Get the indices where the mask is True
        return np.argwhere(mask).flatten()


    def _get_batch_size(self, width: int) -> int:
        """Calculate optimal batch size based on image width."""
        # Use the predefined mapping to get the batch size
        for min_width, divisor in self.MAP_DIMS_TO_SIZE:
            if width >= min_width:
                return max(1, width // divisor)
        return 1
    

    def _compute_energy(self, image: np.ndarray) -> np.ndarray:
        """Compute energy map using configured energy method."""
        # Compute the energy table using the specified method
        return self.method(image)
    
    
    def _compute_costs(self, energy: np.ndarray) -> np.ndarray:
        """Compute cumulative cost table using dynamic programming."""
        
        # Initialize the costs table with the energy values
        costs = energy.astype(np.float32, copy=True)
        height, width = energy.shape
        # Iterate through each row to compute cumulative costs
        for i in range(1, height):
            prev = costs[i-1]
            curr = costs[i]
            
            # Update the interiors and boundaries with minimum costs
            curr[1:-1] += np.minimum(np.minimum(prev[:-2], prev[1:-1]), prev[2:])
            curr[0] += min(prev[0], prev[1])
            curr[-1] += min(prev[-1], prev[-2])
            
        return costs # return costs table
    
    
    def _compute_seams(self, energy: np.ndarray, costs: np.ndarray) -> np.ndarray:
        """Backtrack through cost table to find minimum energy seam."""
        seams = np.zeros(energy.shape, dtype=bool)
        
        # Find the index of the minimum cost pixel in the last row
        prev = int(np.argmin(costs[-1]))
        
        # Set the last index of the seam to the minimum
        seams[-1, prev] = True
        height, width = energy.shape[:2]
        # Backtrack to find the seam path
        for i in range(height-2, -1, -1):
            # Find the bounds and indices for the current seam
            left_bound = max(0, prev - 1)
            right_bound = min(width, prev + 2)
            min_index = int(np.argmin(costs[i, left_bound:right_bound]))
            
            # Update the seam
            seams[i, left_bound + min_index] = True
            
            if costs[i, left_bound + min_index] == np.inf:
                # If the cost is infinite, skip this seam
                return np.zeros_like(seams, dtype=bool)
            
            # Update the previous column index for the next iteration
            prev = left_bound + min_index
        
        # Only change the energy values after finding a valid seam
        energy[seams] = np.inf

        return seams # return seams mask