export SIMGRID_URL=https://framagit.org/simgrid/simgrid/-/archive/v3_13/simgrid-v3_13.tar.gz

# Update and install dependencies
apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    build-essential \
    cmake \
    git \
    libboost-dev \
    libboost-all-dev

# Download and extract SimGrid
wget -O simgrid.tar.gz $SIMGRID_URL
tar -xzf simgrid.tar.gz

mkdir -p /simgrid-v3_13/build
cd /simgrid-v3_13/build

# Build SimGrid
cmake -DCMAKE_INSTALL_PREFIX=/usr/local \
    -Denable_documentation=OFF \
    -Denable_compile_optimizations=ON ..

make -j$(nproc)
make install
make clean

# Remove build dependencies
apt-get autoremove -y \
    libboost-dev \
    libboost-all-dev && \
    apt-get autoclean && \
    apt-get clean

cd /usr/src/python_dependencies