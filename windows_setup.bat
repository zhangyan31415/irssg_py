@echo off
echo === Windows Build Setup Script (Complete) ===

rem 安装构建所需的 Python 包
echo === Installing Python packages ===
pip install delvewheel ninja -q

echo === Installing MSYS2 ===
if not exist "C:\msys64" (
    echo "MSYS2 not found, downloading and installing..."
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/msys2/msys2-installer/releases/download/2024-01-13/msys2-x86_64-20240113.exe' -OutFile 'msys2-installer.exe'"
    echo "Running MSYS2 installer..."
    msys2-installer.exe --accept-messages --accept-licenses --confirm-command --root C:\msys64
    echo "MSYS2 installation completed"
) else (
    echo "MSYS2 already exists at C:\msys64"
)

echo === Installing MSYS2 UCRT64 toolchain ===
echo "Updating MSYS2..."
C:\msys64\usr\bin\pacman.exe -Syu --noconfirm

echo "Installing compilers and LAPACK..."
C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-lapack

echo === Setting up environment ===
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
set "CPATH=C:\msys64\ucrt64\include"
set "LIBRARY_PATH=C:\msys64\ucrt64\lib"

rem 设置环境变量到GitHub Actions环境
echo "PATH=C:\msys64\ucrt64\bin;%PATH%" >> %GITHUB_ENV%
echo "CPATH=C:\msys64\ucrt64\include" >> %GITHUB_ENV%
echo "LIBRARY_PATH=C:\msys64\ucrt64\lib" >> %GITHUB_ENV%

rem 同时设置到当前会话
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
set "CPATH=C:\msys64\ucrt64\include"
set "LIBRARY_PATH=C:\msys64\ucrt64\lib"

echo === Verifying installation ===
echo "Checking GCC..."
C:\msys64\ucrt64\bin\gcc.exe --version
echo "Checking GFortran..."
C:\msys64\ucrt64\bin\gfortran.exe --version

echo === Checking LAPACK installation ===
if exist "C:\msys64\ucrt64\bin\liblapack.dll" (
    echo "✅ liblapack.dll found"
    dir "C:\msys64\ucrt64\bin\liblapack.dll"
) else (
    echo "❌ liblapack.dll NOT found!"
)

echo === Checking all critical libraries ===
echo "LAPACK:"
if exist "C:\msys64\ucrt64\bin\liblapack.dll" echo "  ✅ liblapack.dll"
if exist "C:\msys64\ucrt64\bin\libgfortran-5.dll" echo "  ✅ libgfortran-5.dll"
if exist "C:\msys64\ucrt64\bin\libquadmath-0.dll" echo "  ✅ libquadmath-0.dll"
if exist "C:\msys64\ucrt64\bin\libgcc_s_seh-1.dll" echo "  ✅ libgcc_s_seh-1.dll"
if exist "C:\msys64\ucrt64\bin\libwinpthread-1.dll" echo "  ✅ libwinpthread-1.dll"

echo === Setup Complete ===
echo "PATH: %PATH%"
echo "MSYS2 PATH: C:\msys64\ucrt64\bin" 