FROM mcr.microsoft.com/devcontainers/base:ubuntu-18.04

ARG SIMGRID_URL=https://framagit.org/simgrid/simgrid/-/archive/v3_13/simgrid-v3_13.tar.gz

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install \
    python3 \
    python3-pip \
    build-essential \
    cmake \
    libboost-dev \
    libboost-all-dev

# Download and extract SimGrid
RUN wget -O simgrid.tar.gz $SIMGRID_URL
RUN tar -xzf simgrid.tar.gz

RUN mkdir -p /simgrid-v3_13/build
WORKDIR /simgrid-v3_13/build

# Build SimGrid
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr/local \
    -Denable_documentation=OFF \
    -Denable_compile_optimizations=ON ..

RUN make -j$(nproc)
RUN make install
RUN make clean

# Remove build dependencies
RUN apt-get autoremove -y \
    libboost-dev \
    libboost-all-dev && \
    apt-get autoclean && \
    apt-get clean