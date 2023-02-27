FROM mcr.microsoft.com/devcontainers/base:bullseye

ARG SIMGRID_URL=https://framagit.org/simgrid/simgrid/-/archive/v3_13/simgrid-v3_13.tar.gz

ENV DEBIAN_FRONTEND=noninteractive

# - Install SimGrid's dependencies
# - Compile and install SimGrid itself
RUN echo "DOWNLOAD_URL: ${SIMGRID_URL}" && \
    apt-get update && apt upgrade -y && apt install -y wget && \
    mkdir /source && cd /source && \
    wget ${SIMGRID_URL} && \
    tar xf simgrid-* && rm simgrid-*tar.gz && \
    cd simgrid-* && \
    apt install -y g++ gcc git valgrind gfortran libboost-dev libboost-all-dev libeigen3-dev cmake dpkg-dev python3-dev pybind11-dev && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/ -Denable_documentation=OFF -Denable_smpi=ON -Denable_compile_optimizations=ON . && \
    make -j4 && \
    mkdir debian/ && touch debian/control && dpkg-shlibdeps --ignore-missing-info lib/*.so -llib/ -O/tmp/deps && \
    make install && make clean && \
    apt remove -y  g++ gcc git valgrind default-jdk gfortran libboost-dev libboost-all-dev libeigen3-dev cmake dpkg-dev wget python3-dev pybind11-dev && \
    apt install `sed -e 's/shlibs:Depends=//' -e 's/([^)]*)//g' -e 's/,//g' /tmp/deps` && \
    apt autoremove -y && apt autoclean && apt clean

# Build tools and python3
RUN apt-get install -y build-essential cmake python3-pip python3-venv

ENV DEBIAN_FRONTEND=dialog