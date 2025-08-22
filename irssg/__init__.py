"""
IRSSG - Irreducible Representations of Space Groups

A Python wrapper for the IRSSG Fortran program that calculates
irreducible representations of space groups for crystallographic analysis.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import IRSSG, calculate_irreps
from .utils import read_vasp_output, read_wavecar

__all__ = [
    "IRSSG",
    "calculate_irreps", 
    "read_vasp_output",
    "read_wavecar",
]

