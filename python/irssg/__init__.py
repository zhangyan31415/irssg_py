"""
IRSSG - Irreducible Representations of Space Groups

A Python wrapper for the IRSSG Fortran program that calculates
irreducible representations of space groups for crystallographic analysis.
"""

import os
import sys

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Automatically set IRSSG_DATA_PATH to point to the installed data directory
def _setup_data_path():
    """Set up the data path environment variable for Fortran code"""
    # Get the directory where this package is installed
    package_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for data directory in various possible locations
    possible_paths = [
        os.path.join(package_dir, 'data', 'kLittleGroups'),
        os.path.join(package_dir, '..', 'data', 'kLittleGroups'),
        os.path.join(package_dir, '..', '..', 'data', 'kLittleGroups'),
    ]
    
    # Set the environment variable to the first existing path
    for path in possible_paths:
        if os.path.exists(path):
            os.environ['IRSSG_DATA_PATH'] = path
            break
    else:
        # If no data directory found, set to current working directory
        os.environ['IRSSG_DATA_PATH'] = './kLittleGroups'

# Set up data path when package is imported
_setup_data_path()

from .core import IRSSG, run_irssg

__all__ = [
    "IRSSG",
    "run_irssg",
]

