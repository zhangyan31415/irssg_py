project('irssg', 'fortran', 'cpp',
  version : '0.1.0',
  license : 'MIT',
  meson_version : '>=0.64.0',
  default_options : [
    'buildtype=release',
    'cpp_std=c++17',
  ]
)

# Get Fortran compiler
fortran_compiler = meson.get_compiler('fortran')

# Force legacy Fortran with no line length limits - this must work!
legacy_flags = [
  '-std=legacy',
  '-ffree-line-length-none',
  '-O2',
  '-fPIC'
]

# Add all flags at once - this should override any default settings
add_project_arguments(legacy_flags, language: 'fortran')

# Python dependency
py_mod = import('python')
py3 = py_mod.find_installation('python3', pure: false)
py3_dep = py3.dependency()

# NumPy dependency
np_dep = dependency('numpy', required: false)
if not np_dep.found()
  np_dep = py3.dependency()
endif

# BLAS/LAPACK dependency - required for Fortran code
blas_dep = dependency('openblas', required: true)
if not blas_dep.found()
  blas_dep = dependency('blas', required: true)
endif

# LAPACK is required for zheev_ function
lapack_dep = dependency('lapack', required: true)
if not lapack_dep.found()
  message('LAPACK not found, trying to find it in OpenBLAS...')
  # Some OpenBLAS builds include LAPACK functions
  lapack_dep = dependency('openblas', required: true)
endif

# Compile lib_ssg library
lib_ssg_sources = files(
  'fortran/lib/lib_comms.f90',
  'fortran/lib/lib_bilbao.f90',
  'fortran/lib/lib_chrct.f90',
  'fortran/lib/invreal33.f90',
  'fortran/lib/invmati.f90',
  'fortran/lib/irrep_ssg.f90',
  'fortran/lib/mathlib.f90',
)

lib_ssg = static_library('irssg_lib',
  lib_ssg_sources,
  dependencies: [blas_dep, lapack_dep],
  include_directories: include_directories('fortran/lib'),
)

# Compile src_irssg modules
src_irssg_sources = files(
  'fortran/src/comms.f90',
  'fortran/src/init.f90',
  'fortran/src/get_ssg.f90',
  'fortran/src/comprel.f90',
  'fortran/src/linear_rep.f90',
  'fortran/src/wave_data.f90',
)

src_irssg_lib = static_library('irssg_src',
  src_irssg_sources,
  dependencies: [blas_dep, lapack_dep],
  link_with: [lib_ssg],
  include_directories: [
    include_directories('fortran/src'),
    include_directories('fortran/lib'),
  ],
)

# Build the main Fortran executable
irssg_exe = executable('irssg',
  'fortran/src/main.f90',
  dependencies: [blas_dep, lapack_dep],
  link_with: [lib_ssg, src_irssg_lib],
  include_directories: [
    include_directories('fortran/src'),
    include_directories('fortran/lib'),
  ],
  install: true,
  install_dir: py3.get_install_dir() / 'irssg' / 'bin'
)

# Install Python package files
py3.install_sources([
  'python/irssg/__init__.py',
  'python/irssg/core.py',
  'python/irssg/cli.py',
  'python/irssg/utils.py',
],
  subdir: 'irssg'
)

# Install data files
install_subdir('fortran/lib/kLittleGroups', 
  install_dir: py3.get_install_dir() / 'irssg' / 'data', 
  strip_directory: false,
  install_tag: 'runtime')

# Subdir for Python package
subdir('python')