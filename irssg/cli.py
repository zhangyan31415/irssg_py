#!/usr/bin/env python3
"""
Command-line interface for IRSSG package
"""

import argparse
import sys
import os
from pathlib import Path
from .core import IRSSG


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="IRSSG - Irreducible Representations of Space Groups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  irssg                           # Process all k-points and bands
  irssg -k 1 5                   # Process k-points 1-5
  irssg -b 10 20                 # Process bands 10-20
  irssg -k 1 5 -b 10 20         # Process k-points 1-5, bands 10-20
  irssg -w /path/to/vasp/output  # Use different working directory
  irssg --outcar my_outcar       # Use custom OUTCAR filename
  irssg --wavecar my_wavecar     # Use custom WAVECAR filename
        """
    )
    
    parser.add_argument(
        '-k', '--kpoints',
        nargs=2,
        type=int,
        metavar=('START', 'END'),
        help='K-point range to process (1-based indexing)'
    )
    
    parser.add_argument(
        '-b', '--bands',
        nargs=2,
        type=int,
        metavar=('START', 'END'),
        help='Band range to process (1-based indexing)'
    )
    
    parser.add_argument(
        '-w', '--work-dir',
        type=str,
        help='Working directory containing VASP output files'
    )
    
    parser.add_argument(
        '--outcar',
        type=str,
        default='OUTCAR',
        help='OUTCAR filename (default: OUTCAR)'
    )
    
    parser.add_argument(
        '--wavecar',
        type=str,
        default='WAVECAR',
        help='WAVECAR filename (default: WAVECAR)'
    )
    
    parser.add_argument(
        '--irssg-path',
        type=str,
        help='Path to IRSSG Fortran executable'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for results'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate input files only (no calculation)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize IRSSG
        irssg = IRSSG(work_dir=args.work_dir, irssg_path=args.irssg_path)
        
        if args.verbose:
            print(f"Working directory: {irssg.work_dir}")
            print(f"IRSSG executable: {irssg.irssg_path}")
            print(f"OUTCAR file: {args.outcar}")
            print(f"WAVECAR file: {args.wavecar}")
        
        # Read VASP output files
        try:
            info = irssg.read_vasp_output(args.outcar, args.wavecar)
            if args.verbose:
                print(f"VASP calculation info:")
                print(f"  Title: {info['title']}")
                print(f"  K-points: {info['num_k']}")
                print(f"  Bands: {info['num_bands']}")
                print(f"  Spin: {info['nspin']}")
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Validate only mode
        if args.validate:
            print("Input files validated successfully!")
            return
        
        # Determine k-point and band ranges
        k_start, k_end = 1, info['num_k']
        if args.kpoints:
            k_start, k_end = args.kpoints
            if k_start < 1 or k_end > info['num_k']:
                print(f"Error: K-point range {k_start}-{k_end} is out of bounds (1-{info['num_k']})", file=sys.stderr)
                sys.exit(1)
        
        band_start, band_end = 1, info['num_bands']
        if args.bands:
            band_start, band_end = args.bands
            if band_start < 1 or band_end > info['num_bands']:
                print(f"Error: Band range {band_start}-{band_end} is out of bounds (1-{info['num_bands']})", file=sys.stderr)
                sys.exit(1)
        
        if args.verbose:
            print(f"Processing k-points {k_start}-{k_end}, bands {band_start}-{band_end}")
        
        # Run calculation
        result = irssg.calculate_irreps(
            k_start=k_start,
            k_end=k_end,
            band_start=band_start,
            band_end=band_end,
            output_file=args.output
        )
        
        # Handle results
        if result['success']:
            print("IRSSG calculation completed successfully!")
            if args.verbose:
                print(f"Command executed: {result['command']}")
                print(f"K-point range: {result['k_range']}")
                print(f"Band range: {result['band_range']}")
            
            if args.output:
                print(f"Results saved to: {args.output}")
            else:
                # Print first few lines of output
                lines = result['stdout'].strip().split('\n')
                if lines:
                    print("\nFirst few lines of output:")
                    for line in lines[:10]:
                        print(f"  {line}")
                    if len(lines) > 10:
                        print(f"  ... ({len(lines)-10} more lines)")
        else:
            print("IRSSG calculation failed!", file=sys.stderr)
            if 'error' in result:
                print(f"Error: {result['error']}", file=sys.stderr)
            if result['stderr']:
                print(f"STDERR: {result['stderr']}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

