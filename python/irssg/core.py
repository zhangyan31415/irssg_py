"""
Core Python wrapper for IRSSG Fortran program
"""

import os
import subprocess
import numpy as np
from pathlib import Path
from typing import Optional, List


class IRSSG:
    """
    Python wrapper for IRSSG (Irreducible Representations of Space Groups)
    
    This class provides a simple interface to call the IRSSG Fortran program.
    """
    
    def __init__(self, irssg_path: Optional[str] = None):
        """
        Initialize IRSSG wrapper
        
        Parameters
        ----------
        irssg_path : str, optional
            Path to the IRSSG Fortran executable
            If None, tries to find it automatically
        """
        if irssg_path is None:
            # Try to find the executable automatically
            possible_paths = [
                "irssg",  # Current directory
                "src_irssg/irssg",
                "../src_irssg/irssg",
                "../../src_irssg/irssg",
                "fortran/src/irssg",  # New project structure
                "../fortran/src/irssg",
                "../../fortran/src/irssg"
            ]
            
            # Also check system PATH
            import shutil
            system_irssg = shutil.which("irssg")
            if system_irssg:
                possible_paths.insert(0, system_irssg)
            
            for path in possible_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    irssg_path = path
                    break
        
        if irssg_path is None or not os.path.exists(irssg_path):
            raise FileNotFoundError(f"IRSSG executable not found. Please specify the correct path.")
        
        # Expand user directory and resolve path
        self.irssg_path = Path(os.path.expanduser(irssg_path)).resolve()
        
        if not os.access(self.irssg_path, os.X_OK):
            raise PermissionError(f"IRSSG executable {self.irssg_path} is not executable")
    
    def run(self, work_dir: Optional[str] = None, **kwargs) -> subprocess.CompletedProcess:
        """
        Run the IRSSG Fortran program
        
        Parameters
        ----------
        work_dir : str, optional
            Working directory containing VASP output files
        **kwargs : 
            Additional arguments to pass to the IRSSG program
        
        Returns
        -------
        subprocess.CompletedProcess
            Result of the subprocess call
        """
        if work_dir is None:
            work_dir = os.getcwd()
        
        # Build command line arguments
        cmd = [str(self.irssg_path)]
        
        # Add any additional arguments
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, bool):
                    if value:
                        cmd.append(f"--{key}")
                else:
                    cmd.append(f"--{key}")
                    cmd.append(str(value))
        
        # Run the command
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        return result
    
    def validate_input(self, work_dir: Optional[str] = None) -> bool:
        """
        Validate that required input files exist
        
        Parameters
        ----------
        work_dir : str, optional
            Working directory to check
            
        Returns
        -------
        bool
            True if all required files exist
        """
        if work_dir is None:
            work_dir = os.getcwd()
        
        required_files = ["OUTCAR", "WAVECAR"]
        
        for filename in required_files:
            filepath = os.path.join(work_dir, filename)
            if not os.path.exists(filepath):
                print(f"Warning: Required file {filename} not found in {work_dir}")
                return False
        
        return True


def run_irssg(irssg_path: Optional[str] = None, work_dir: Optional[str] = None, **kwargs) -> subprocess.CompletedProcess:
    """
    Convenience function to run IRSSG
    
    Parameters
    ----------
    irssg_path : str, optional
        Path to the IRSSG executable
    work_dir : str, optional
        Working directory
    **kwargs : 
        Additional arguments for IRSSG
        
    Returns
    -------
    subprocess.CompletedProcess
        Result of the subprocess call
    """
    irssg = IRSSG(irssg_path)
    return irssg.run(work_dir, **kwargs)

