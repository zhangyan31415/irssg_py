@echo off
echo === Windows Build Setup Script (LAPACK only) ===

rem 安装构建所需的 Python 包
pip install delvewheel ninja -q

echo === Installing MSYS2 UCRT64 toolchain ===
C:\msys64\usr\bin\pacman.exe -Syu --noconfirm
C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-lapack

echo === Setting up MSYS2 PATH ===
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
echo Verifying MSYS2 compilers...
gfortran --version
gcc --version

echo === Setting up final environment ===
rem Add MSYS2 to PATH
set "PATH=C:\msys64\ucrt64\bin;%PATH%"

rem Configure development paths
set "CPATH=C:\msys64\ucrt64\include"
set "LIBRARY_PATH=C:\msys64\ucrt64\lib"

echo Final verification...
gfortran --version
gcc --version

echo === Setup Complete === 