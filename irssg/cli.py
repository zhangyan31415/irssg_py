"""
Command-line interface for IRSSG package
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .core import IRSSG, calculate_irreps
from .utils import validate_input_files, list_available_space_groups


def main(args: Optional[List[str]] = None) -> int:
    """
    Main command-line interface
    
    Parameters
    ----------
    args : list of str, optional
        Command line arguments. If None, uses sys.argv[1:]
        
    Returns
    -------
    int
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="IRSSG - Irreducible Representations of Space Groups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  irssg                                    # Run with default files (OUTCAR, WAVECAR)
  irssg -k 1 5                            # Process k-points 1-5
  irssg -b 10 20                          # Process bands 10-20
  irssg -w /path/to/workdir               # Use different working directory
  irssg --outcar my_outcar --wavecar my_wavecar  # Use custom file names
        """
    )
    
    parser.add_argument(
        '-w', '--work-dir',
        type=str,
        help='Working directory containing VASP files (default: current directory)'
    )
    
    parser.add_argument(
        '--outcar',
        type=str,
        default='OUTCAR',
        help='Path to OUTCAR file (default: OUTCAR)'
    )
    
    parser.add_argument(
        '--wavecar',
        type=str,
        default='WAVECAR',
        help='Path to WAVECAR file (default: WAVECAR)'
    )
    
    parser.add_argument(
        '-k', '--k-points',
        type=int,
        nargs=2,
        metavar=('START', 'END'),
        help='K-point range to process (1-based indexing)'
    )
    
    parser.add_argument(
        '-b', '--bands',
        type=int,
        nargs=2,
        metavar=('START', 'END'),
        help='Band range to process (1-based indexing)'
    )
    
    parser.add_argument(
        '--list-space-groups',
        action='store_true',
        help='List available space group numbers and exit'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate input files and exit'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Handle special commands
    if parsed_args.list_space_groups:
        try:
            space_groups = list_available_space_groups()
            print("Available space group numbers:")
            for sg in space_groups:
                print(f"  {sg}")
            return 0
        except Exception as e:
            print(f"Error listing space groups: {e}", file=sys.stderr)
            return 1
    
    if parsed_args.validate:
        try:
            is_valid = validate_input_files(
                outcar_path=parsed_args.outcar,
                wavecar_path=parsed_args.wavecar,
                work_dir=parsed_args.work_dir
            )
            if is_valid:
                print("✓ Input files are valid")
                return 0
            else:
                print("✗ Input files are invalid", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error validating files: {e}", file=sys.stderr)
            return 1
    
    # Main calculation
    try:
        if parsed_args.verbose:
            print("IRSSG - Irreducible Representations of Space Groups")
            print("=" * 50)
        
        # Validate input files
        if parsed_args.verbose:
            print("Validating input files...")
        
        is_valid = validate_input_files(
            outcar_path=parsed_args.outcar,
            wavecar_path=parsed_args.wavecar,
            work_dir=parsed_args.work_dir
        )
        
        if not is_valid:
            print("Error: Invalid input files", file=sys.stderr)
            return 1
        
        # Initialize IRSSG
        if parsed_args.verbose:
            print("Initializing IRSSG...")
        
        irssg = IRSSG(work_dir=parsed_args.work_dir)
        
        # Read VASP output
        if parsed_args.verbose:
            print("Reading VASP output files...")
        
        file_info = irssg.read_vasp_output(
            outcar_path=parsed_args.outcar,
            wavecar_path=parsed_args.wavecar
        )
        
        if parsed_args.verbose:
            print(f"VASP calculation info:")
            print(f"  Number of k-points: {file_info['num_k']}")
            print(f"  Number of bands: {file_info['num_bands']}")
            print(f"  Spin polarization: {file_info['nspin']}")
        
        # Determine k-point and band ranges
        k_start, k_end = None, None
        if parsed_args.k_points:
            k_start, k_end = parsed_args.k_points
        
        band_start, band_end = None, None
        if parsed_args.bands:
            band_start, band_end = parsed_args.bands
        
        if parsed_args.verbose:
            print("Calculating irreducible representations...")
            if k_start and k_end:
                print(f"  K-point range: {k_start}-{k_end}")
            if band_start and band_end:
                print(f"  Band range: {band_start}-{band_end}")
        
        # Run calculation
        results = irssg.calculate_irreps(
            k_start=k_start,
            k_end=k_end,
            band_start=band_start,
            band_end=band_end
        )
        
        if parsed_args.verbose:
            print(f"Calculation completed successfully!")
            print(f"Processed {len(results)} k-point(s)")
            
            for result in results:
                print(f"  K-point {result['k_point']}: {result['k_name']} "
                      f"({result['k_coords'][0]:.3f}, {result['k_coords'][1]:.3f}, {result['k_coords'][2]:.3f})")
                print(f"    Irreducible representations: {result['irrep_num']}")
                print(f"    Little group size: {result['num_litt_group']}")
                print(f"    Unitary operations: {result['num_litt_group_unitary']}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nCalculation interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed_args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

