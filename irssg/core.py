"""
Core Python wrapper for IRSSG Fortran library
"""

import os
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import tempfile
import json


class IRSSG:
    """
    Python wrapper for IRSSG (Irreducible Representations of Space Groups)
    
    This class provides a high-level interface to the IRSSG Fortran program
    for calculating irreducible representations of space groups in crystallography.
    """
    
    def __init__(self, work_dir: Optional[str] = None, irssg_path: Optional[str] = None):
        """
        Initialize IRSSG wrapper
        
        Parameters
        ----------
        work_dir : str, optional
            Working directory containing VASP output files (OUTCAR, WAVECAR)
            If None, uses current directory
        irssg_path : str, optional
            Path to the IRSSG Fortran executable
            If None, tries to find it in the package
        """
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        
        # Find IRSSG executable
        if irssg_path:
            self.irssg_path = Path(irssg_path)
        else:
            # Try to find the executable in the package
            package_dir = Path(__file__).parent
            self.irssg_path = package_dir / "src_irssg" / "irssg"
            
            # If not found in package, try system PATH
            if not self.irssg_path.exists():
                self.irssg_path = Path("irssg")
        
        if not self.irssg_path.exists():
            raise FileNotFoundError(f"IRSSG executable not found at {self.irssg_path}")
        
        self.initialized = False
        self.file_info = None
        
    def read_vasp_output(self, outcar_path: str = "OUTCAR", wavecar_path: str = "WAVECAR") -> Dict:
        """
        Read VASP output files and get basic information
        
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
        
        # Read basic information from OUTCAR
        info = self._read_outcar_info(outcar_file)
        self.file_info = info
        self.initialized = True
        
        return info
    
    def _read_outcar_info(self, outcar_file: Path) -> Dict:
        """Read basic information from OUTCAR file"""
        info = {
            'num_sym': 0,
            'num_k': 0,
            'num_bands': 0,
            'nspin': 1,
            'title': '',
            'lattice_vectors': None,
            'kpoints': [],
            'energies': []
        }
        
        with open(outcar_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Read title
            if 'SYSTEM =' in line:
                info['title'] = line.split('=')[1].strip()
            
            # Read number of k-points and bands
            if 'k-points' in line and 'NKPTS' in line:
                parts = line.split()
                for j, part in enumerate(parts):
                    if part == 'NKPTS':
                        info['num_k'] = int(parts[j+1])
                    elif part == 'NBANDS':
                        info['num_bands'] = int(parts[j+1])
            
            # Read spin polarization
            if 'ISPIN' in line:
                info['nspin'] = int(line.split('=')[1])
            
            # Read lattice vectors
            if 'direct lattice vectors' in line:
                lattice = []
                for j in range(3):
                    if i + j + 1 < len(lines):
                        parts = lines[i + j + 1].split()
                        if len(parts) >= 3:
                            lattice.append([float(x) for x in parts[:3]])
                if len(lattice) == 3:
                    info['lattice_vectors'] = np.array(lattice)
        
        return info
    
    def calculate_irreps(self, 
                        k_start: int = 1, 
                        k_end: Optional[int] = None,
                        band_start: Optional[int] = None,
                        band_end: Optional[int] = None,
                        output_file: Optional[str] = None) -> Dict:
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
        output_file : str, optional
            Output file path for results
            
        Returns
        -------
        dict
            Results and status information
        """
        if not self.initialized:
            raise RuntimeError("IRSSG not initialized. Call read_vasp_output() first.")
        
        if k_end is None:
            k_end = self.file_info['num_k']
        if band_start is None:
            band_start = 1
        if band_end is None:
            band_end = self.file_info['num_bands']
        
        # Build command line arguments
        cmd = [str(self.irssg_path)]
        
        # Add k-point range if specified
        if k_start != 1 or k_end != self.file_info['num_k']:
            cmd.extend(['-nk', str(k_start), str(k_end)])
        
        # Add band range if specified
        if band_start != 1 or band_end != self.file_info['num_bands']:
            cmd.extend(['-nb', str(band_start), str(band_end)])
        
        # Change to working directory for execution
        original_dir = os.getcwd()
        os.chdir(self.work_dir)
        
        try:
            # Run IRSSG program
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            output = {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'k_range': (k_start, k_end),
                'band_range': (band_start, band_end),
                'command': ' '.join(cmd)
            }
            
            # If output file specified, save results
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                    if result.stderr:
                        f.write("\n\nSTDERR:\n")
                        f.write(result.stderr)
            
            return output
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Execution timeout',
                'k_range': (k_start, k_end),
                'band_range': (band_start, band_end),
                'command': ' '.join(cmd)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'k_range': (k_start, k_end),
                'band_range': (band_start, band_end),
                'command': ' '.join(cmd)
            }
        finally:
            os.chdir(original_dir)
    
    def run_simple(self, k_points: Optional[List[int]] = None, 
                   bands: Optional[Tuple[int, int]] = None) -> Dict:
        """
        Simple interface to run IRSSG with minimal parameters
        
        Parameters
        ----------
        k_points : list of int, optional
            List of k-point indices to process
        bands : tuple of int, optional
            (start_band, end_band) range
            
        Returns
        -------
        dict
            Results from IRSSG execution
        """
        if k_points:
            k_start, k_end = min(k_points), max(k_points)
        else:
            k_start, k_end = 1, self.file_info['num_k'] if self.initialized else 1
        
        if bands:
            band_start, band_end = bands
        else:
            band_start, band_end = 1, self.file_info['num_bands'] if self.initialized else 1
        
        return self.calculate_irreps(k_start, k_end, band_start, band_end)


def calculate_irreps(outcar_path: str = "OUTCAR",
                    wavecar_path: str = "WAVECAR",
                    k_points: Optional[List[int]] = None,
                    bands: Optional[Tuple[int, int]] = None,
                    work_dir: Optional[str] = None) -> Dict:
    """
    Convenience function to calculate irreducible representations
    
    Parameters
    ----------
    outcar_path : str
        Path to OUTCAR file
    wavecar_path : str
        Path to WAVECAR file
    k_points : list of int, optional
        List of k-point indices to process
    bands : tuple of int, optional
        (start_band, end_band) range
    work_dir : str, optional
        Working directory
        
    Returns
    -------
    dict
        Results from IRSSG execution
    """
    irssg = IRSSG(work_dir=work_dir)
    irssg.read_vasp_output(outcar_path, wavecar_path)
    
    if k_points:
        k_start, k_end = min(k_points), max(k_points)
    else:
        k_start, k_end = 1, irssg.file_info['num_k']
    
    if bands:
        band_start, band_end = bands
    else:
        band_start, band_end = 1, irssg.file_info['num_k']
    
    return irssg.calculate_irreps(k_start, k_end, band_start, band_end)

