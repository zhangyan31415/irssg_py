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
  irssg                           # Run IRSSG with default settings
  irssg --irssg-path /path/to/irssg  # Use custom IRSSG executable
  irssg --work-dir /path/to/vasp/output  # Use different working directory
        """
    )
    
    parser.add_argument(
        '--irssg-path',
        type=str,
        help='Path to IRSSG Fortran executable'
    )
    
    parser.add_argument(
        '--work-dir',
        type=str,
        default=os.getcwd(),
        help='Working directory containing VASP output files (default: current directory)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate input files before running'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    # Add any other arguments that the Fortran program might accept
    parser.add_argument(
        '--args',
        nargs='*',
        help='Additional arguments to pass to IRSSG Fortran program'
    )
    
    args = parser.parse_args()
    
    try:
        # Create IRSSG wrapper
        irssg = IRSSG(irssg_path=args.irssg_path)
        
        if args.verbose:
            print(f"Working directory: {args.work_dir}")
            print(f"IRSSG executable: {irssg.irssg_path}")
        
        # Validate input files if requested
        if args.validate:
            if not irssg.validate_input(args.work_dir):
                print("Validation failed. Please check your input files.")
                sys.exit(1)
            if args.verbose:
                print("Input validation passed.")
        
        # Prepare arguments for Fortran program
        fortran_args = {}
        if args.args:
            # Parse additional arguments
            for arg in args.args:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    fortran_args[key] = value
                else:
                    fortran_args[arg] = True
        
        # Run IRSSG
        if args.verbose:
            print("Running IRSSG Fortran program...")
        
        result = irssg.run(args.work_dir, **fortran_args)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        # Exit with appropriate code
        sys.exit(result.returncode)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

