FROM ubuntu:22.04

# Set the working directory for CheckMate
WORKDIR /home/ubuntu

# Update and upgrade packages
RUN apt-get update && apt-get upgrade -y

# Install dependencies
RUN apt-get install -y \
    git \
    autoconf \
    perl \
    graphviz \
    clang \
    python3.10 \
    python3-pip \
    wget \
    libboost-dev \
    build-essential \
    g++ \
    ninja-build \
    gdb \
    libncurses5 \
    libncursesw5 \
    libtinfo5 \
    libpython2.7 \
    rsync \
    clangd \
    ffmpeg libsm6 libxext6

# Copy project files to CheckMate folder
COPY . /home/ubuntu/CheckMate

RUN git clone https://github.com/rafayy769/fused-checkmate.git /home/ubuntu/fused-checkmate

# Install CMake
ARG CMAKE_VERSION=3.15.4
RUN wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-Linux-x86_64.sh && \
    chmod +x cmake-${CMAKE_VERSION}-Linux-x86_64.sh && \
    ./cmake-${CMAKE_VERSION}-Linux-x86_64.sh --skip-license --prefix=/usr/local && \
    rm cmake-${CMAKE_VERSION}-Linux-x86_64.sh

# Install Egypt tool
WORKDIR /home/ubuntu/egypt
RUN wget https://www.gson.org/egypt/download/egypt-1.11.tar.gz && \
    tar -xvf egypt-1.11.tar.gz && \
    cd egypt-1.11 && \
    perl Makefile.PL && \
    make && \
    make install

# Build fused-checkmate project
WORKDIR /home/ubuntu/fused-checkmate
RUN mkdir build && cd build

WORKDIR /home/ubuntu/fused-checkmate/build
RUN cmake .. -GNinja -DINSTALL_DEPENDENCIES=ON -DINSTALL_TARGET_TOOLCHAINS=ON -DEP_INSTALL_DIR=/home/ubuntu/.local && ninja

# Set environment variables for toolchains
ENV TOOLCHAIN_DIR=/home/ubuntu/.local
ENV ARM_GCC_ROOT="${TOOLCHAIN_DIR}/arm-gcc"
ENV MSP430_GCC_ROOT="${TOOLCHAIN_DIR}/msp430-gcc"
ENV MSP430_INC="${TOOLCHAIN_DIR}/msp430-inc"
ENV PATH="${TOOLCHAIN_DIR}/msp430-gcc/bin:${TOOLCHAIN_DIR}/arm-gcc/bin:${PATH}"

# Finally build fused
RUN cmake .. -GNinja -DINSTALL_DEPENDENCIES=OFF && ninja \
    && cp fused /home/ubuntu/CheckMate/fusedBin

WORKDIR /home/ubuntu/CheckMate

# Build the eval-apps
RUN mkdir -p eval-apps/build && cd eval-apps/build && cmake .. -DTARGET_ARCH=msp430 && make

# Install Python dependencies
RUN pip install -r requirements.txt

RUN mkdir -p target

# Default command to start a terminal for the user
CMD ["/bin/bash"]
