#!/usr/bin/env bash

# Project details (can be moved to a separate configuration file)
PROJECT_URL="https://github.com/rafayy769/fused-checkmate.git"
CMAKE_VERSION="3.15.4"  # Update to the latest stable version
TOOLCHAIN_DIR="${HOME}/.local"

# Parse command line arguments
while getopts ":cbipth" opt; do
  case "$opt" in
    c) clone_repo=true ;;
    b) build_deps=true ;;
    i) install_cmake=true ;;
    p) project_deps=true ;;
    t) set_env_vars=true ;;
    h)
      echo "Usage: ./script.sh [-cbipt]"
      echo "  -c  Clone the Git repository"
      echo "  -b  Install build dependencies"
      echo "  -i  Install CMake"
      echo "  -p  Install toolchain and project dependencies"
      echo "  -t  Set environment variables"
      exit 0 ;;
    \?)
      echo "Invalid option: -$OPTARG"
      exit 1 ;;
  esac
done

# Default values
clone_repo="${clone_repo:-true}"
build_deps="${build_deps:-true}"
install_cmake="${install_cmake:-true}"
project_deps="${project_deps:-true}"
set_env_vars="${set_env_vars:-true}"

# Perform actions based on command line arguments
if "$clone_repo"; then
  git clone "$PROJECT_URL" || exit 1
  cd fused-checkmate
fi

if "$build_deps"; then
  sudo apt install libboost-dev build-essential g++ ninja-build git gdb libncurses5 libncursesw5 libtinfo5 libpython2.7 || exit 1
fi

if "$install_cmake"; then
  wget https://github.com/Kitware/CMake/releases/download/v$CMAKE_VERSION/cmake-$CMAKE_VERSION-Linux-x86_64.sh || exit 1
  chmod +x cmake-$CMAKE_VERSION-Linux-x86_64.sh
  sudo ./cmake-$CMAKE_VERSION-Linux-x86_64.sh --skip-license --prefix=/usr/local || exit 1
  rm cmake-$CMAKE_VERSION-Linux-x86_64.sh
fi

if "$project_deps"; then
  mkdir build && cd build
  cmake .. -GNinja -DINSTALL_DEPENDENCIES=ON -DINSTALL_TARGET_TOOLCHAINS=ON 
  ninja|| exit 1
fi

if "$set_env_vars"; then
  echo "** This step sets environment variables. Proceed with caution if unsure. **"
  
  export ARM_GCC_ROOT="${TOOLCHAIN_DIR}/arm-gcc"
  export MSP430_GCC_ROOT="${TOOLCHAIN_DIR}/msp430-gcc"
  export MSP430_INC="${TOOLCHAIN_DIR}/msp430-inc"
  export PATH="${TOOLCHAIN_DIR}/msp430-gcc/bin:$PATH"
  export PATH="${TOOLCHAIN_DIR}/arm-gcc/bin:$PATH"
  
fi

# in fused/build
cmake .. -GNinja -DINSTALL_DEPENDENCIES=OFF
ninja

echo "Script completed."
