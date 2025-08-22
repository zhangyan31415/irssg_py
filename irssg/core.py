"""
Core Python wrapper for IRSSG Fortran library
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

try:
    from . import _irssg
except ImportError:
    _irssg = None


class IRSSG:
    """
    Python wrapper for IRSSG (Irreducible Representations of Space Groups)
    
    This class provides a high-level interface to the IRSSG Fortran library
    for calculating irreducible representations of space groups in crystallography.
    """
    
    def __init__(self, work_dir: Optional[str] = None):
        """
        Initialize IRSSG wrapper
        
        Parameters
        ----------
        work_dir : str, optional
            Working directory containing VASP output files (OUTCAR, WAVECAR)
            If None, uses current directory
        """
        if _irssg is None:
            raise ImportError("IRSSG Fortran library not available. Please install the package.")
        
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.initialized = False
        self.file_info = None
        
    def read_vasp_output(self, outcar_path: str = "OUTCAR", wavecar_path: str = "WAVECAR") -> Dict:
        """
        Read VASP output files and initialize the calculation
        
        Parameters
        ----------
        outcar_path : str
            Path to OUTCAR file
        wavecar_path : str
            Path to WAVECAR file
            
        Returns
        -------
        dict
            Information about the VASP calculation
        """
        outcar_file = self.work_dir / outcar_path
        wavecar_file = self.work_dir / wavecar_path
        
        if not outcar_file.exists():
            raise FileNotFoundError(f"OUTCAR file not found: {outcar_file}")
        if not wavecar_file.exists():
            raise FileNotFoundError(f"WAVECAR file not found: {wavecar_file}")
        
        # Change to working directory for Fortran file operations
        original_dir = os.getcwd()
        os.chdir(self.work_dir)
        
        try:
            self.file_info = _irssg.read_vasp_files(outcar_path, wavecar_path)
            self.initialized = True
            return self.file_info
        finally:
            os.chdir(original_dir)
    
    def calculate_irreps(self, 
                        k_start: int = 1, 
                        k_end: Optional[int] = None,
                        band_start: Optional[int] = None,
                        band_end: Optional[int] = None) -> List[Dict]:
        """
        Calculate irreducible representations for specified k-points and bands
        
        Parameters
        ----------
        k_start : int
            Starting k-point index (1-based)
        k_end : int, optional
            Ending k-point index (1-based). If None, uses all k-points
        band_start : int, optional
            Starting band index (1-based). If None, uses all bands
        band_end : int, optional
            Ending band index (1-based). If None, uses all bands
            
        Returns
        -------
        list
            List of dictionaries containing results for each k-point
        """
        if not self.initialized:
            raise RuntimeError("IRSSG not initialized. Call read_vasp_output() first.")
        
        # Change to working directory for Fortran file operations
        original_dir = os.getcwd()
        os.chdir(self.work_dir)
        
        try:
            results = _irssg.calculate_irreducible_representations(
                k_start=k_start,
                k_end=k_end,
                band_start=band_start,
                band_end=band_end
            )
            return results
        finally:
            os.chdir(original_dir)
    
    def run(self, 
            k_points: Optional[List[int]] = None,
            bands: Optional[Tuple[int, int]] = None) -> List[Dict]:
        """
        Run complete IRSSG calculation
        
        Parameters
        ----------
        k_points : list of int, optional
            List of k-point indices to process. If None, processes all k-points
        bands : tuple of int, optional
            (start_band, end_band) tuple. If None, processes all bands
            
        Returns
        -------
        list
            List of dictionaries containing results for each k-point
        """
        # Read VASP output if not already done
        if not self.initialized:
            self.read_vasp_output()
        
        # Determine k-point range
        if k_points is None:
            k_start = 1
            k_end = None
        else:
            k_start = min(k_points)
            k_end = max(k_points)
        
        # Determine band range
        band_start, band_end = None, None
        if bands is not None:
            band_start, band_end = bands
        
        return self.calculate_irreps(
            k_start=k_start,
            k_end=k_end,
            band_start=band_start,
            band_end=band_end
        )


def calculate_irreps(outcar_path: str = "OUTCAR",
                    wavecar_path: str = "WAVECAR",
                    work_dir: Optional[str] = None,
                    k_points: Optional[List[int]] = None,
                    bands: Optional[Tuple[int, int]] = None) -> List[Dict]:
    """
    Convenience function to run IRSSG calculation
    
    Parameters
    ----------
    outcar_path : str
        Path to OUTCAR file
    wavecar_path : str
        Path to WAVECAR file
    work_dir : str, optional
        Working directory
    k_points : list of int, optional
        List of k-point indices to process
    bands : tuple of int, optional
        (start_band, end_band) tuple
        
    Returns
    -------
    list
        List of dictionaries containing results for each k-point
    """
    irssg = IRSSG(work_dir=work_dir)
    return irssg.run(k_points=k_points, bands=bands)

