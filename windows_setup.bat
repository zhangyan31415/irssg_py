@echo off
echo === Windows Build Setup Script (LAPACK only) ===
echo Current working directory: %CD%
echo Current PATH: %PATH%

rem 安装构建所需的 Python 包
echo === Installing Python packages ===
pip install delvewheel ninja -q

echo === Checking MSYS2 installation status ===
if exist "C:\msys64" (
    echo "✅ MSYS2 directory exists: C:\msys64"
    dir "C:\msys64"
) else (
    echo "❌ MSYS2 directory NOT found: C:\msys64"
    echo "This is a problem - MSYS2 must be pre-installed!"
    exit /b 1
)

if exist "C:\msys64\usr\bin\pacman.exe" (
    echo "✅ pacman found: C:\msys64\usr\bin\pacman.exe"
) else (
    echo "❌ pacman NOT found: C:\msys64\usr\bin\pacman.exe"
    echo "This is a problem - MSYS2 installation is incomplete!"
    exit /b 1
)

echo === Installing MSYS2 UCRT64 toolchain ===
echo "Running: C:\msys64\usr\bin\pacman.exe -Syu --noconfirm"
C:\msys64\usr\bin\pacman.exe -Syu --noconfirm
if errorlevel 1 (
    echo "❌ pacman update failed!"
    exit /b 1
)

echo "Running: C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-lapack mingw-w64-ucrt-x86_64-gcc-libs mingw-w64-ucrt-x86_64-libgccjit mingw-w64-ucrt-x86_64-libquadmath"
C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-lapack mingw-w64-ucrt-x86_64-gcc-libs mingw-w64-ucrt-x86_64-libgccjit mingw-w64-ucrt-x86_64-libquadmath
if errorlevel 1 (
    echo "❌ pacman install failed!"
    exit /b 1
)

echo === Checking installed packages ===
echo "Checking gcc:"
if exist "C:\msys64\ucrt64\bin\gcc.exe" (
    echo "✅ gcc found: C:\msys64\ucrt64\bin\gcc.exe"
    dir "C:\msys64\ucrt64\bin\gcc.exe"
) else (
    echo "❌ gcc NOT found: C:\msys64\ucrt64\bin\gcc.exe"
)

echo "Checking gfortran:"
if exist "C:\msys64\ucrt64\bin\gfortran.exe" (
    echo "✅ gfortran found: C:\msys64\ucrt64\bin\gfortran.exe"
    dir "C:\msys64\ucrt64\bin\gfortran.exe"
) else (
    echo "❌ gfortran NOT found: C:\msys64\ucrt64\bin\gfortran.exe"
    echo "Listing ucrt64/bin contents:"
    dir "C:\msys64\ucrt64\bin\*gfortran*" 2>nul || echo "No gfortran files found"
)

echo === Setting up MSYS2 PATH ===
echo "Original PATH: %PATH%"
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
echo "Updated PATH: %PATH%"

echo === Verifying MSYS2 compilers ===
echo "Testing gcc:"
gcc --version
if errorlevel 1 (
    echo "❌ gcc --version failed!"
    echo "Current PATH: %PATH%"
    where gcc || echo "gcc not found in PATH"
)

echo "Testing gfortran:"
gfortran --version
if errorlevel 1 (
    echo "❌ gfortran --version failed!"
    echo "Current PATH: %PATH%"
    where gfortran || echo "gfortran not found in PATH"
)

echo === Setting up final environment ===
rem Add MSYS2 to PATH
set "CPATH=C:\msys64\ucrt64\include"
set "LIBRARY_PATH=C:\msys64\ucrt64\lib"

echo "Final PATH: %PATH%"
echo "CPATH: %CPATH%"
echo "LIBRARY_PATH: %LIBRARY_PATH%"

echo === Final verification ===
echo "Final gfortran test:"
gfortran --version
if errorlevel 1 (
    echo "❌ Final gfortran test failed!"
    echo "This means the build will fail!"
    exit /b 1
) else (
    echo "✅ gfortran is working correctly!"
)

echo "Final gcc test:"
gcc --version
if errorlevel 1 (
    echo "❌ Final gcc test failed!"
    echo "This means the build will fail!"
    exit /b 1
) else (
    echo "✅ gcc is working correctly!"
)

echo === Setup Complete ===
echo "All compilers are working correctly!"
echo "PATH: %PATH%" 