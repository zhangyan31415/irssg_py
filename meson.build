project('irssg', 'fortran', 'cpp', 'c',
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

# Get C compiler for Windows checks
c_compiler = meson.get_compiler('c')

# Set macOS deployment target for compatibility
if host_machine.system() == 'darwin'
  macos_target = run_command('python', '-c', 'import os; print(os.environ.get("MACOSX_DEPLOYMENT_TARGET", "14.0"))', check: false).stdout().strip()
  message('Setting macOS deployment target: ' + macos_target)
  add_project_arguments('-mmacosx-version-min=' + macos_target, language: 'fortran')
  add_project_arguments('-mmacosx-version-min=' + macos_target, language: 'cpp')
endif

# Initialize link_args for platform-specific linking
link_args = []

# Force legacy Fortran with no line length limits - this must work!
legacy_flags = [
  '-std=legacy',
  '-ffree-line-length-none',
  '-O2',
  '-fPIC'
]

# Add all flags at once - this should override any default settings
add_project_arguments(legacy_flags, language: 'fortran')

# Initialize fortran_args for MPI and other flags
fortran_args = []

# Add MPI preprocessor definition if MPI is found
# For wheels/packaging builds, we use runtime MPI detection only
is_wheel_build = run_command('python', '-c', 'import os; print(os.environ.get("CIBUILDWHEEL", "false"))', check: false).stdout().strip()

# Enable MPI on all platforms where MPI is available
# Note: mpi_dep will be defined later, so we check platform first
if host_machine.system() == 'darwin' or host_machine.system() == 'linux'
  fortran_args += ['-DMPI']
  
  if is_wheel_build == '1'
    message('Building wheel with compile-time MPI support for ' + host_machine.system())
  else
    message('Building with compile-time MPI support for ' + host_machine.system())
  endif
else
  message('Building in serial mode - MPI not found or not supported.')
endif

# Python dependency
py_mod = import('python')
py3 = py_mod.find_installation('python3', pure: false)
py3_dep = py3.dependency()

# NumPy dependency
np_dep = dependency('numpy', required: false)
if not np_dep.found()
  np_dep = py3.dependency()
endif

# LAPACK dependency - we only need zheev function
is_cibuildwheel = run_command('python', '-c', 'import os; print(os.environ.get("CIBUILDWHEEL", "false"))', check: false).stdout().strip()

if is_cibuildwheel == '1'
  # In cibuildwheel environment, use manual linking only
  message('cibuildwheel detected: using manual library linking only')
  blas_dep = dependency('', required: false)  # Force not found
  lapack_dep = dependency('', required: false)  # Force not found
else
  # Normal build environment, use meson detection
  # We only need LAPACK for zheev, not full BLAS
  lapack_dep = dependency('lapack', required: false)
  if not lapack_dep.found()
    message('LAPACK not found, will use manual linking')
  endif
  
  # Minimal BLAS dependency (only if LAPACK requires it)
  blas_dep = dependency('', required: false)  # Force not found
endif

# Platform-specific configuration
message('Host machine: ' + host_machine.system())
message('Build machine: ' + build_machine.system())

# For Windows, add additional system libraries and ensure consistent toolchain
if host_machine.system() == 'windows'
  if fortran_compiler.get_id().startswith('gcc')
    message('Windows: Using MinGW/GCC toolchain with enhanced DLL support')
    # Add runtime libraries with explicit paths for better DLL discovery
    link_args += ['-LC:/msys64/mingw64/bin', '-LC:/msys64/mingw64/lib']
    link_args += ['-lgfortran', '-lquadmath', '-lm', '-lwinpthread']
    
    # Add runtime DLL search paths
    link_args += ['-Wl,--enable-auto-import']
    link_args += ['-Wl,--enable-runtime-pseudo-reloc']
    
    message('Windows: Added MinGW runtime libraries and DLL search paths')
    
    # Ensure we use MinGW linker, not MSVC
    if c_compiler.get_id() != 'gcc'
      warning('Windows: C compiler is not GCC, this may cause linking issues')
      warning('Consider setting CC=gcc and CXX=g++ for consistent toolchain'    )
  endif
endif

if build_machine.system() == 'windows' and fortran_compiler.get_id().startswith('intel')
  mpi_lib_dir = 'C:/Program Files (x86)/Intel/oneAPI/mpi/latest/lib/'
  link_args += ['-LIBPATH:' + mpi_lib_dir, 'impi.lib']
endif
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

if is_cibuildwheel == '1'
  # In cibuildwheel environment, use manual linking
  lib_ssg = static_library('irssg_lib',
    lib_ssg_sources,
    include_directories: include_directories('fortran/lib'),
  )
else
  # Normal build environment, use dependency system
  lib_ssg = static_library('irssg_lib',
    lib_ssg_sources,
    dependencies: [blas_dep, lapack_dep],
    include_directories: include_directories('fortran/lib'),
  )
endif

# Compile src_irssg modules
src_irssg_sources = files(
  'fortran/src/comms.f90',
  'fortran/src/init.f90',
  'fortran/src/get_ssg.f90',
  'fortran/src/comprel.f90',
  'fortran/src/linear_rep.f90',
  'fortran/src/wave_data.f90',
)

if is_cibuildwheel == '1'
  # In cibuildwheel environment, use manual linking
  src_irssg_lib = static_library('irssg_src',
    src_irssg_sources,
    link_with: [lib_ssg],
    include_directories: [
      include_directories('fortran/src'),
      include_directories('fortran/lib'),
    ],
  )
else
  # Normal build environment, use dependency system
  src_irssg_lib = static_library('irssg_src',
    src_irssg_sources,
    dependencies: [blas_dep, lapack_dep],
    link_with: [lib_ssg],
    include_directories: [
      include_directories('fortran/src'),
      include_directories('fortran/lib'),
    ],
  )
endif

# Build the main Fortran executable
if is_cibuildwheel == '1'
  # In cibuildwheel environment, use platform-specific linking
  if host_machine.system() == 'darwin'
    # macOS: use Homebrew LAPACK paths (simplified approach)
    # LAPACK包含了我们需要的zheev函数
    lapack_lib_path = ''
    if is_cibuildwheel == '1'
      # 在cibuildwheel环境中，使用标准路径
      lapack_lib_path = '/opt/homebrew/opt/lapack/lib'
    else
      # 在本地环境中，尝试自动检测
      pkgconfig = find_program('pkg-config', required: false)
      if pkgconfig.found()
        lapack_lib_path = run_command(pkgconfig, '--variable=libdir', 'lapack', check: false).stdout().strip()
      endif
      if lapack_lib_path == ''
        # 回退到常见路径
        common_paths = ['/opt/homebrew/opt/lapack/lib', '/usr/local/opt/lapack/lib', '/opt/local/lib']
        foreach path : common_paths
          if run_command('test', '-d', path, check: false).returncode() == 0
            lapack_lib_path = path
            break
          endif
        endforeach
      endif
    endif
    
    if lapack_lib_path == ''
      error('Could not find LAPACK library path on macOS')
    endif
    
    message('Using LAPACK library path: ' + lapack_lib_path)
    
    irssg_exe = executable('irssg',
      'fortran/src/main.f90',
      link_with: [lib_ssg, src_irssg_lib],
      include_directories: [
        include_directories('fortran/src'),
        include_directories('fortran/lib'),
      ],
      link_args: ['-L' + lapack_lib_path, '-llapack', '-Wl,-rpath,' + lapack_lib_path],
      install: true,
      install_dir: py3.get_install_dir() / 'irssg' / 'bin'
    )
  elif host_machine.system() == 'windows'
    # Windows: Manually add MPI dependency for MS-MPI (MinGW compatible)
    message('Windows: Manually configuring MPI dependency for MS-MPI')
    
    # Set MPI include and lib directories for Meson
    mpi_inc_dir = 'C:/msys64/ucrt64/include'
    mpi_lib_dir = 'C:/msys64/ucrt64/lib'
    
    mpi_dep = declare_dependency(
      include_directories: include_directories(mpi_inc_dir),
      link_args: ['-L' + mpi_lib_dir, '-lmsmpi'] # Link against the generated libmsmpi.a
    )
    message('Windows: MPI dependency configured.')
    
    irssg_exe = executable('irssg',
      'fortran/src/main.f90',
      link_with: [lib_ssg, src_irssg_lib],
      dependencies: [mpi_dep],
      include_directories: [
        include_directories('fortran/src'),
        include_directories('fortran/lib'),
      ],
      link_args: ['-LC:/msys64/ucrt64/lib', '-llapack', '-lgfortran'],
      fortran_args: ['-DMPI', '-I' + 'C:/msys64/ucrt64/include'],
      install: true,
      install_dir: py3.get_install_dir() / 'irssg' / 'bin'
    )
  else
    # Linux: use system paths
    irssg_exe = executable('irssg',
      'fortran/src/main.f90',
      link_with: [lib_ssg, src_irssg_lib],
      include_directories: [
        include_directories('fortran/src'),
        include_directories('fortran/lib'),
      ],
      link_args: ['-L/usr/lib64', '-llapack', '-Wl,-rpath,/usr/lib64'],
      install: true,
      install_dir: py3.get_install_dir() / 'irssg' / 'bin'
    )
  endif
else
  # Normal build environment, use dependency system
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
endif

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