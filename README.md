# scheduling-simulator
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
docker run --rm -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/src && python3 generate_simulation_data.py"
```

The resulting files will be available on the host after executing the command.

## Tests
To execute the tests, run:
```bash
docker run --rm -it -v $(pwd):/usr/src/app build-simgrid bash -c "cd /usr/src/app/ && python3 -m pytest"
```