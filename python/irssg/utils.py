"""
Utility functions for IRSSG package
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def read_vasp_output(outcar_path: str = "OUTCAR") -> Dict:
    """
    Read basic information from VASP OUTCAR file
    
    Parameters
    ----------
    outcar_path : str
        Path to OUTCAR file
        
    Returns
    -------
    dict
        Dictionary containing VASP calculation information
    """
    outcar_file = Path(outcar_path)
    if not outcar_file.exists():
        raise FileNotFoundError(f"OUTCAR file not found: {outcar_file}")
    
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


def read_wavecar(wavecar_path: str = "WAVECAR") -> Dict:
    """
    Read basic information from VASP WAVECAR file
    
    Parameters
    ----------
    wavecar_path : str
        Path to WAVECAR file
        
    Returns
    -------
    dict
        Dictionary containing WAVECAR information
    """
    wavecar_file = Path(wavecar_path)
    if not wavecar_file.exists():
        raise FileNotFoundError(f"WAVECAR file not found: {wavecar_file}")
    
    info = {
        'nrecl': 0,
        'nspin': 1,
        'nprec': 0,
        'nkpts': 0,
        'nbands': 0,
        'ecut': 0.0,
        'lattice_vectors': None,
        'kpoints': [],
        'energies': []
    }
    
    # WAVECAR is a binary file, so we need to read it carefully
    # This is a simplified version - the full implementation would need
    # to handle the binary format properly
    
    try:
        with open(wavecar_file, 'rb') as f:
            # Read header information
            # This is a placeholder - actual implementation would parse binary data
            pass
    except Exception as e:
        print(f"Warning: Could not read WAVECAR file: {e}")
    
    return info


def validate_input_files(outcar_path: str = "OUTCAR", 
                        wavecar_path: str = "WAVECAR",
                        work_dir: Optional[str] = None) -> bool:
    """
    Validate that required input files exist and are readable
    
    Parameters
    ----------
    outcar_path : str
        Path to OUTCAR file
    wavecar_path : str
        Path to WAVECAR file
    work_dir : str, optional
        Working directory
        
    Returns
    -------
    bool
        True if all files are valid, False otherwise
    """
    base_dir = Path(work_dir) if work_dir else Path.cwd()
    
    outcar_file = base_dir / outcar_path
    wavecar_file = base_dir / wavecar_path
    
    if not outcar_file.exists():
        print(f"Error: OUTCAR file not found: {outcar_file}")
        return False
    
    if not wavecar_file.exists():
        print(f"Error: WAVECAR file not found: {wavecar_file}")
        return False
    
    # Check if files are readable
    try:
        with open(outcar_file, 'r') as f:
            f.read(100)  # Read first 100 characters
    except Exception as e:
        print(f"Error: Cannot read OUTCAR file: {e}")
        return False
    
    try:
        with open(wavecar_file, 'rb') as f:
            f.read(100)  # Read first 100 bytes
    except Exception as e:
        print(f"Error: Cannot read WAVECAR file: {e}")
        return False
    
    return True


def get_data_path() -> Path:
    """
    Get the path to the IRSSG data directory
    
    Returns
    -------
    Path
        Path to the data directory containing kLittleGroups files
    """
    package_dir = Path(__file__).parent
    data_dir = package_dir / 'data'
    
    if not data_dir.exists():
        raise FileNotFoundError(f"IRSSG data directory not found: {data_dir}")
    
    return data_dir


def list_available_space_groups() -> List[int]:
    """
    List available space group numbers in the kLittleGroups data
    
    Returns
    -------
    list
        List of available space group numbers
    """
    data_dir = get_data_path()
    kLittleGroups_dir = data_dir / 'kLittleGroups'
    
    if not kLittleGroups_dir.exists():
        return []
    
    space_groups = []
    for file in kLittleGroups_dir.glob('kLG_*.data'):
        try:
            # Extract space group number from filename
            sgn = int(file.stem.split('_')[1])
            space_groups.append(sgn)
        except (ValueError, IndexError):
            continue
    
    return sorted(space_groups)


def check_space_group_availability(space_group: int) -> bool:
    """
    Check if data is available for a specific space group
    
    Parameters
    ----------
    space_group : int
        Space group number
        
    Returns
    -------
    bool
        True if data is available, False otherwise
    """
    available_sgs = list_available_space_groups()
    return space_group in available_sgs

