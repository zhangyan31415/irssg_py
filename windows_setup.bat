@echo off
echo === Windows Build Setup Script (Simplified) ===

rem 安装构建所需的 Python 包
echo === Installing Python packages ===
pip install delvewheel ninja -q

echo === Installing MSYS2 UCRT64 toolchain ===
echo "Updating MSYS2..."
C:\msys64\usr\bin\pacman.exe -Syu --noconfirm

echo "Installing compilers and LAPACK..."
C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-lapack

echo === Setting up environment ===
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
set "CPATH=C:\msys64\ucrt64\include"
set "LIBRARY_PATH=C:\msys64\ucrt64\lib"

echo === Verifying installation ===
gcc --version
gfortran --version

echo === Setup Complete ===
echo "PATH: %PATH%" 