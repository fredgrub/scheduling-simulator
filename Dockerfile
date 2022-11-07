FROM debian:11 AS builder
ARG SIMGRID_URL=https://framagit.org/simgrid/simgrid/-/archive/v3_13/simgrid-v3_13.tar.gz

# Update and install dependencies
RUN apt-get update && apt-get install -y \
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

# Clean up
RUN apt-get autoremove -y \
    wget \
    build-essential \
    cmake \
    git \
    libboost-dev \
    libboost-all-dev && \
    apt-get autoclean && \
    apt-get clean

FROM python:3.10-slim-bullseye
ENV filename first-model/lublin_256.swf
ENV deployment_file first-model/deployment_cluster.xml
ENV platform_file first-model/simple_cluster.xml
ENV s_size 16
ENV q_size 32
ENV num_tuples 1
ENV num_trials 100

COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/include /usr/local/include
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /usr/src/app

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Compile simulator
WORKDIR src/
RUN make

CMD ["sh", "-c", "python generate_simulation_data.py ${filename} ${deployment_file} ${platform_file} ${s_size} ${q_size} ${num_tuples} ${num_trials}"]