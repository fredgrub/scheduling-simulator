FROM ubuntu:18.04
ARG SIMGRID_URL=https://framagit.org/simgrid/simgrid/-/archive/v3_13/simgrid-v3_13.tar.gz

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    build-essential \
    cmake \
    git \
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

WORKDIR /usr/src/python_dependencies

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt