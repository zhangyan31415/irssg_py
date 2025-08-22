#!/usr/bin/env python3
"""
IRSSG Command Line Interface

This script provides a command-line interface to IRSSG.
It can be used as a standalone executable.
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

def find_irssg_executable():
    """Find the IRSSG Fortran executable"""
    # First try to find it in the package's bin directory
    package_dir = Path(__file__).resolve().parent
    exe_path = package_dir / 'bin' / 'irssg'
    
    if exe_path.exists() and os.access(exe_path, os.X_OK):
        return str(exe_path)
    
    # Fallback to system PATH
    import shutil
    system_path = shutil.which('irssg')
    if system_path:
        return system_path
    
    raise FileNotFoundError("IRSSG executable not found. Please ensure the package is properly installed.")

def main():
    """Main command line interface"""
    parser = argparse.ArgumentParser(
        description="IRSSG Python Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  irssg                    # Run with default irssg.in
  irssg -o output.log      # Redirect output to file
  irssg --validate         # Validate input files
  irssg --version          # Show version information

Note: This is a Python wrapper for the IRSSG Fortran code.
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate input files and exit'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        default='irssg.in',
        help='Input file path (default: irssg.in)'
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("IRSSG Python Interface v0.1.0")
        return 0
    
    if args.validate:
        # Validate input files
        input_file = Path(args.input_file)
        if not input_file.exists():
            print(f"Error: Input file '{input_file}' not found")
            return 1
        
        print(f"Input file '{input_file}' is valid")
        return 0
    
    # Find the IRSSG executable
    try:
        irssg_exe = find_irssg_executable()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Prepare command
    cmd = [irssg_exe]
    
    # Set up output redirection
    if args.output:
        try:
            with open(args.output, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            print(f"Error writing to output file: {e}")
            return 1
    else:
        # Run and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())

