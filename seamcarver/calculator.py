"""Calculator for seam carving Operations"""

# Import standard library packages
import numpy as np
# import project specific packages
from .methods import EnergyMethod, GradientEnergy


class SeamCalculator:
    """A class to calculate the seam for seam carving operations.
    
    This class is responsible for calculating the seam based on the energy
    of the image and the specified direction (vertical or horizontal).
    
    Attributes:
        image (np.ndarray): Image data as a numpy array.
        energy_tbl (np.ndarray): Energy table of the image.
        energy_cst (np.ndarray): Energy cost table for seam calculation.
        seam (np.ndarray): Indices of the seam in the image.
        method (EnergyMethod): Method to calculate the energy of the image.
        
    Note: 
        This class assumes that the image is always in a vertical orientation
        for seam carving. For horizontal seams, the image should be transposed
        before passing it to the methods.
    """

    # Class constants
    MAP_DIMS_TO_SIZE: list[tuple[int, int]] = [ # (min_dimension, percentage)
        (1000, 8),  # 12.5% per batch for images >= 1000 pixels
        (500, 10),  # 10.0% per batch for images >= 500 pixels
        (100, 10),  # ~8.3% per batch for images >= 100 pixels
        (20, 15),   # ~6.7% per batch for images >= 0 pixels
        (0, 20),    #  5.0% per batch for images < 20 pixels
    ]

    # Class attributes
    image: np.ndarray
    """np.ndarray: image data as a numpy array."""
    energy_tbl: np.ndarray
    """np.ndarray: energy table of the image."""
    energy_cst: np.ndarray
    """np.ndarray: energy cost table for seam calculation."""
    seam: np.ndarray
    """np.ndarray: indices of the seam in the image."""
    method: EnergyMethod
    """EnergyMethod: method to calculate the energy of the image."""


    def __init__(self, method: EnergyMethod = GradientEnergy()):
        """Initialize the SeamCalculator with an energy method."""
        self.method = method
        
    
    def __call__(
        self,
        image: np.ndarray,
        seams: int,
        batched: bool,
    ) -> np.ndarray:
        """Find and return seams in the image as a boolean mask."""
         
        # Get a copy of the image for processing
        self.image = image.copy()
        
        if batched:
            # Get the minimum dimension of the image
            dimension = self.image.shape[1]
            
            SIZE = self.MAP_DIMS_TO_SIZE
            
            # Determine batch size based on image dimensions
            if dimension >= SIZE[0][0]: batch_size = dimension // SIZE[0][1]   # 12.5%
            elif dimension >= SIZE[1][0]: batch_size = dimension // SIZE[1][1] # 10.0%
            elif dimension >= SIZE[2][0]: batch_size = dimension // SIZE[2][1] # ~8.3%
            elif dimension >= SIZE[3][0]: batch_size = dimension // SIZE[3][1] # ~6.7%
            elif dimension >= SIZE[4][0]: batch_size = dimension // SIZE[4][1] #  5.0%
            else: raise ValueError("Invalid image dimensions for seam carving.")
            
            # Initialize result mask and indices tracking
            result_mask = np.zeros(self.image.shape[:2], dtype=bool)
            
            # Compute energy once
            self._compute_energy()
            
            remaining_seams = seams
            while remaining_seams > 0:
                for _ in range(min(batch_size, remaining_seams)):
                    # Reset seam for each individual seam
                    self.seam = np.zeros(self.image.shape[:2], dtype=bool)
                    
                    self._compute_cost()
                    self._compute_seam()
                    result_mask = result_mask | self.seam
                
                remaining_seams -= batch_size
            
            return result_mask
        
        else:
            # Single seam case
            self.seam = np.zeros(self.image.shape[:2], dtype=bool)
            self._compute_energy()
            self._compute_cost()
            self._compute_seam()
            return self.seam


    def mask_to_index(self, mask: np.ndarray) -> np.ndarray:
        """Convert a boolean mask to a list of indices."""
        # Get the indices where the mask is True
        return np.argwhere(mask).flatten()


    def _compute_energy(self) -> None:
        """Compute the energy table for the image using the specified method.
    
        This method calculates the energy of each pixel in the image based on
        the chosen energy method (e.g., GradientEnergy).
        """
        
        # Compute the energy table using the specified method
        self.energy_tbl = self.method.compute_energy(self.image)
    
    
    def _compute_cost(self) -> None:
        """Compute cumulative minimum cost table using dynamic programming.
    
        For each pixel, computes the minimum cost path from the top row,
        considering the current pixel's energy plus the minimum of:
        - Direct parent (same column)
        - Left diagonal parent  
        - Right diagonal parent
        """
        
        # Initialize the energy cost table with the energy table
        self.energy_cst = self.energy_tbl.copy()
        
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
        """Backtrack through cost table to find minimum energy seam.
    
        Starts from the minimum cost pixel in the bottom row and works
        upward, choosing the parent pixel that contributed to the minimum cost.
        """
        
        # Find the index of the minimum cost pixel in the last row
        prev = int(np.argmin(self.energy_cst[-1]))
        
        # Set the last index of the seam to the minimum
        self.seam[-1, prev] = True
        self.energy_tbl[-1, prev] = np.inf

        # Backtrack to find the seam path
        for i in range(self.image.shape[0]-2, -1, -1):
            # Find the bounds for the left and right neighbors
            left_bound = max(0, prev - 1)
            right_bound = min(self.image.shape[1], prev + 2)
            loc = int(np.argmin(self.energy_cst[i, left_bound:right_bound]))
            
            # Update the seam
            self.seam[i, left_bound + loc] = True
            self.energy_tbl[i, left_bound + loc] = np.inf
            
            # Update the previous column index for the next iteration
            prev = left_bound + loc