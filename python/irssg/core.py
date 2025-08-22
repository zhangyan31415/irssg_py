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
                    # Check if it's not a Python script
                    try:
                        with open(path, 'rb') as f:
                            first_line = f.readline().decode('utf-8', errors='ignore').strip()
                            if not first_line.startswith('#!'):
                                irssg_path = path
                                break
                    except:
                        # If we can't read it, assume it's a binary
                        irssg_path = path
                        break
        
        if irssg_path is None or not os.path.exists(irssg_path):
            raise FileNotFoundError(f"IRSSG executable not found. Please specify the correct path.")
        
        # Expand user directory and resolve path
        self.irssg_path = Path(os.path.expanduser(irssg_path)).resolve()
        
        # Final check: ensure it's not a Python script
        try:
            with open(self.irssg_path, 'rb') as f:
                first_line = f.readline().decode('utf-8', errors='ignore').strip()
                if first_line.startswith('#!'):
                    raise FileNotFoundError(f"Found Python script instead of executable: {self.irssg_path}")
        except:
            pass  # If we can't read it, assume it's a binary
        
        if not os.access(self.irssg_path, os.X_OK):
            raise PermissionError(f"IRSSG executable {self.irssg_path} is not executable")
    
    def run(self, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """
        Run the IRSSG program
        
        Parameters
        ----------
        timeout : int, optional
            Timeout in seconds
            
        Returns
        -------
        subprocess.CompletedProcess
            Result of the subprocess call
        """
        if not self.irssg_path:
            raise FileNotFoundError("IRSSG executable not found. Please specify the correct path.")
        
        try:
            result = subprocess.run(
                [self.irssg_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace invalid characters instead of failing
                timeout=timeout,
                cwd=os.getcwd()
            )
            return result
        except subprocess.TimeoutExpired:
            # Kill the process if it times out
            raise subprocess.TimeoutExpired([self.irssg_path], timeout)
        except UnicodeDecodeError as e:
            # Fallback to binary mode if text mode fails
            try:
                result = subprocess.run(
                    [self.irssg_path],
                    capture_output=True,
                    text=False,  # Use binary mode
                    timeout=timeout,
                    cwd=os.getcwd()
                )
                # Try to decode with error handling
                stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
                stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
                
                # Create a new CompletedProcess with decoded text
                return subprocess.CompletedProcess(
                    [self.irssg_path],
                    result.returncode,
                    stdout=stdout,
                    stderr=stderr
                )
            except Exception as fallback_error:
                raise RuntimeError(f"Failed to run IRSSG: {e}. Fallback also failed: {fallback_error}")
    
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

