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

# BLAS/LAPACK dependency - make optional for now
blas_dep = dependency('openblas', required: false)
if not blas_dep.found()
  blas_dep = dependency('blas', required: false)
endif
if not blas_dep.found()
  blas_dep = dependency('mkl', required: false)
endif
if not blas_dep.found()
  # Create a dummy dependency
  blas_dep = declare_dependency()
endif

lapack_dep = dependency('lapack', required: false)
if not lapack_dep.found()
  lapack_dep = dependency('openblas', required: false)
endif
if not lapack_dep.found()
  # Create a dummy dependency
  lapack_dep = declare_dependency()
endif

# Compile lib_ssg library
lib_ssg_sources = [
  'lib_ssg/lib_comms.f90',
  'lib_ssg/lib_bilbao.f90',
  'lib_ssg/lib_chrct.f90',
  'lib_ssg/invreal33.f90',
  'lib_ssg/invmati.f90',
  'lib_ssg/irrep_ssg.f90',
  'lib_ssg/mathlib.f90',
]

lib_ssg = static_library('irssg_lib',
  lib_ssg_sources,
  dependencies: [blas_dep, lapack_dep],
  include_directories: include_directories('lib_ssg'),
)

# Compile src_irssg modules
src_irssg_sources = [
  'src_irssg/comms.f90',
  'src_irssg/init.f90',
  'src_irssg/get_ssg.f90',
  'src_irssg/comprel.f90',
  'src_irssg/linear_rep.f90',
  'src_irssg/wave_data.f90',
]

src_irssg_lib = static_library('irssg_src',
  src_irssg_sources,
  dependencies: [blas_dep, lapack_dep],
  link_with: [lib_ssg],
  include_directories: [
    include_directories('src_irssg'),
    include_directories('lib_ssg'),
  ],
)

# Python extension module - simplified for now
# py3.extension_module('_irssg',
#   'irssg/_irssg.pyx',
#   dependencies: [py3_dep, np_dep, blas_dep, lapack_dep],
#   link_with: [lib_ssg, src_irssg_lib],
#   include_directories: [
#     include_directories('src_irssg'),
#     include_directories('lib_ssg'),
#   ],
#   install: true,
# )

# Install data files
data_files = []
install_data(data_files, install_dir: py3.get_install_dir() / 'irssg' / 'data')

# Subdir for Python package
subdir('irssg')