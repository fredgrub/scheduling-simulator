FROM mcr.microsoft.com/vscode/devcontainers/python:3.10-bullseye

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
    apt remove -y valgrind default-jdk gfortran libboost-dev libboost-all-dev libeigen3-dev dpkg-dev python3-dev pybind11-dev && \
    apt install `sed -e 's/shlibs:Depends=//' -e 's/([^)]*)//g' -e 's/,//g' /tmp/deps` && \
    apt autoremove -y && apt autoclean && apt clean

# Install python3 packages
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt && \
    rm -rf /tmp/pip-tmp