"""Built-in energy methods and the optional class-based interface."""

from .gradient import GradientEnergy
from .interface import EnergyMethod
from .laplacian import LaplacianEnergy
from .sobel import SobelEnergy

__all__ = ["EnergyMethod", "GradientEnergy", "LaplacianEnergy", "SobelEnergy"]
