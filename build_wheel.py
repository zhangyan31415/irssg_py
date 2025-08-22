#!/usr/bin/env python3
"""
Build script for IRSSG wheel package
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False
    print(f"Success: {cmd}")
    return True

def main():
    """Main build function"""
    print("Building IRSSG wheel package...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run from the project root.")
        return 1
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for path in ["build", "dist", "*.egg-info"]:
        if Path(path).exists():
            shutil.rmtree(path)
    
    # Install build dependencies
    print("Installing build dependencies...")
    if not run_command("pip install build meson-python ninja"):
        return 1
    
    # Build the package
    print("Building package...")
    if not run_command("python -m build"):
        return 1
    
    # List built packages
    print("\nBuilt packages:")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.glob("*"):
            print(f"  {file}")
    
    print("\nBuild completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

