# Scheduling Simulator
## Running the code in this repository
### Dependencies
The code in this repository has been tested and executed on Debian Bullseye (11) with the following dependencies:
- SimGrid 3.13
- Python 3.9.2 (+ `requirements.txt`)

There are details in the `Dockerfile` on how to locally compile and install this specific version of SimGrid.

### Using Dev Containers
If you use Visual Studio Code, there is an extension (**Dev Containers**) that allows you to bring VSCode inside the container, providing the runtime environment for the IDE. The `.devcontainer/devcontainer.json` file defines how the environment will be (image, container, extensions, etc.).

In VSCode, just invoke the Command Palette (`F1`) and run **Dev Containers: Open Folder in Container...** to open the current folder in a container.

### Using Docker container
Another way to run the code in this repository is through **Docker**. The first step is to build the current project image, which can be done through the command:
```bash
docker build -t build-simgrid .
```

- TODO: I need to review what's below...

After building the image, the container can be run with different commands. For instance, the `make` command can be used to compile the `simulator` and `tester` C code. To compile them using the container just run:
```bash
docker run --rm -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/src/simulator && make"
docker run --rm -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/src/tester && make"
```

Note that both commands must be executed in the project root, otherwise they will fail.

Running the simulator, for instance, can be done in a similar way:
```bash
docker run --rm -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/src && python3 simulator.py @parameters.txt"
```

Note that it is necessary to pass a file containing the parameters to be simulated. Use the `parameters.txt` file as a template. If the workload used changes, it will be necessary to change the files `deployment_cluster.xml` and `simple_cluster.xml`. Use the information in the table below to make your changes. The resulting files will be available on the host after executing the command.

### Non-exhaustive table

| **ANL**                 | **Curie**                  | **CTC-SP2**              | **HPC2N**              | **SDSC-Blue**              | **SDSC-SP2**              | **Lublin runtimes** | **Lublin estimated**    | 
|-------------------------|----------------------------|--------------------------|------------------------|----------------------------|---------------------------|---------------------|-------------------------|
| ANL-Intrepid-2009-1.swf | CEA-Curie-2011-2.1-cln.swf | CTC-SP2-1996-3.1-cln.swf | HPC2N-2002-2.2-cln.swf | SDSC-BLUE-2000-4.2-cln.swf | SDSC-SP2-1998-4.2-cln.swf | lublin_256/1024.swf | lublin_256/1024_est.swf |
| 163840                  | 93312                      | 338                      | 240                    | 1152                       | 128                       | 256/1024            | 256/1024                |