# Scheduling Simulator (under construction :construction:)
Simulate the scheduling of jobs from a workload model.

## Usage
The compilation and execution of the code is done through a Docker container. The first step is to build the current project image, which can be done through the command:
```bash
docker build -t build-simgrid .
```

After building the image, the container can be run with different commands. The `make` command is used to compile the code. So, to compile the code using the container just run:
```bash
docker run --rm -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/src && make"
```

Note that this command must be executed in the project root, as the volume mounted in the container is the `src` folder. Also, the generated binary will be saved in the `src` folder of the project (on the host).

Running the simulator can be done in a similar way. To run the simulator, just run:
```bash
docker run --rm -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/src && python3 simulator.py @parameters.txt"
```

Note that it is necessary to pass a file containing the parameters to be simulated. Use the `parameters.txt` file as a template. If the workload used changes, it will be necessary to change the files `deployment_cluster.xml` and `simple_cluster.xml`. Use the information in the table below to make your changes. The resulting files will be available on the host after executing the command.

### Information to simulate

| **ANL**                 | **Curie**                  | **CTC-SP2**              | **HPC2N**              | **SDSC-Blue**              | **SDSC-SP2**              | **Lublin runtimes** | **Lublin estimated**    |
|-------------------------|----------------------------|--------------------------|------------------------|----------------------------|---------------------------|---------------------|-------------------------|
| ANL-Intrepid-2009-1.swf | CEA-Curie-2011-2.1-cln.swf | CTC-SP2-1996-3.1-cln.swf | HPC2N-2002-2.2-cln.swf | SDSC-BLUE-2000-4.2-cln.swf | SDSC-SP2-1998-4.2-cln.swf | lublin_256/1024.swf | lublin_256/1024_est.swf |
| 163840                  | 93312                      | 338                      | 240                    | 1152                       | 128                       | 256/1024            | 256/1024                |

## Tests
To execute the tests, run:
```bash
docker run --rm -it -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/ && python3 -m pytest"
```

## Development
I implemented a workflow using Dev Containers that allows development in a functional and productive environment. However, this workflow is totally dependent on VSCode.

To use this workflow you need the `ms-vscode-remote.remote-containers` extension (known as Dev Containers). With the extension already installed and at the root of this project, just call the **Dev Containers: Reopen in Container** command from the command palette and wait the compilation/execution.
