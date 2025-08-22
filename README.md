# IRSSG - Irreducible Representations of Space Groups

A Python wrapper for the IRSSG Fortran program that calculates irreducible representations of space groups for crystallographic analysis.

## Features

- **Python Interface**: Easy-to-use Python API for the IRSSG Fortran library
- **Cross-platform**: Works on Linux and macOS
- **Self-contained**: All dependencies (including BLAS/LAPACK) are bundled in the wheel
- **Command-line Interface**: Simple CLI for batch processing
- **VASP Integration**: Direct support for VASP output files (OUTCAR, WAVECAR)

## Installation

### From PyPI (Recommended)

```bash
pip install irssg
```

### From Source

```bash
git clone https://github.com/yourusername/irssg.git
cd irssg
pip install -e .
```

## Quick Start

### Python API

```python
import irssg

# Initialize IRSSG with VASP output files
irssg_calc = irssg.IRSSG(work_dir="./vasp_output")

# Read VASP files and get calculation info
info = irssg_calc.read_vasp_output("OUTCAR", "WAVECAR")
print(f"Number of k-points: {info['num_k']}")
print(f"Number of bands: {info['num_bands']}")

# Calculate irreducible representations for specific k-points and bands
results = irssg_calc.calculate_irreps(
    k_start=1, k_end=5,      # Process k-points 1-5
    band_start=10, band_end=20  # Process bands 10-20
)

# Or use the convenience function
results = irssg.calculate_irreps(
    outcar_path="OUTCAR",
    wavecar_path="WAVECAR",
    k_points=[1, 2, 3, 4, 5],
    bands=(10, 20)
)
```

### Command Line Interface

```bash
# Basic usage with default files (OUTCAR, WAVECAR)
irssg

# Process specific k-points
irssg -k 1 5

# Process specific bands
irssg -b 10 20

# Use different working directory
irssg -w /path/to/vasp/output

# Use custom file names
irssg --outcar my_outcar --wavecar my_wavecar

# Validate input files
irssg --validate

# List available space groups
irssg --list-space-groups

# Verbose output
irssg -v
```

## Requirements

### System Dependencies

The package automatically handles BLAS/LAPACK dependencies, but you need:

- **Linux**: GCC with Fortran support (`gfortran`)
- **macOS**: Xcode Command Line Tools or GCC

### Python Dependencies

- Python 3.8 or higher
- NumPy
- SciPy

## Input Files

IRSSG requires VASP output files:

- **OUTCAR**: Contains symmetry operations, k-points, and band information
- **WAVECAR**: Contains wavefunction coefficients

## Output

The calculation produces:

- Character tables for each k-point
- Irreducible representation labels
- Compatibility relations between representations
- Detailed analysis output files

## Development

### Building from Source

```bash
# Install build dependencies
pip install build meson-python ninja

# Build the package
python -m build

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Basic import test
python -c "import irssg; print('Success!')"

# Run with test data (if available)
python -m irssg.cli --validate
```

## License

MIT License - see LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{irssg2024,
  title={IRSSG: Irreducible Representations of Space Groups},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/irssg}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:

1. Check the [documentation](https://github.com/yourusername/irssg#readme)
2. Search existing [issues](https://github.com/yourusername/irssg/issues)
3. Create a new issue with a minimal example

## Acknowledgments

This package wraps the original IRSSG Fortran program. The underlying algorithms and methods are based on crystallographic symmetry analysis and group theory.

# irssg_py
