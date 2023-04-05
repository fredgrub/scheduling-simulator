# An experimental analysis of regression-obtained HPC scheduling heuristics (source material)

This repository contains the companion material for the research work **An experimental analysis of regression-obtained HPC scheduling heuristics**.
The authors are:
Lucas Rosa, Danilo Carastan-Santos and Alfredo Goldman

## Inital setup
### Dependencies
The code in this repository has been tested and executed on Debian Bullseye (11) with the following dependencies:
- SimGrid 3.13
- Python 3.9.2 (+ `requirements.txt`)

There are details in the `Dockerfile` on how to locally compile and install this specific version of SimGrid.

### The canonical way
Once every dependency is installed, you must run the `initialize.py` script. This script download the remaining files and compile the C code. On the root of the repository:
```bash
python initialize.py
```

### Using Dev Containers
If you use Visual Studio Code, there is an extension (**Dev Containers**) that allows you to bring VSCode inside the container, providing the runtime environment for the IDE. The `.devcontainer/devcontainer.json` file defines how the environment will be (image, container, extensions, etc.).

In VSCode, just invoke the Command Palette (`F1`) and run **Dev Containers: Open Folder in Container...** to open the current folder in a container. Then, run the `initialize.py` script.

### Using Docker container
Another way to run the code in this repository is through **Docker**. The first step is to build the current project image, which can be done through the command:
```bash
docker build -t build-simgrid .
```

After building the image, the container can be used to run different commands. For instance, you can run the `initialize.py` script as following:
```bash
docker run --rm -v $(pwd):/workspaces/scheduling-simulator/ build-simgrid bash -c "python /workspaces/scheduling-simulator/initialize.py"
```

Note that this command must be executed in the project root, otherwise it will fail.

## The modules
### Simulator
This module is used to generate the distribution $\operatorname{score}(p, q, r)$. The simulation parameters are described as a simple python dictionary at the start of `simulator.py` file. Any entry can be modified to satisfy your needs. 

The simulations could take some time, depending on the chosen parameters. Because of this, you should execute the code using the `nohup <code> &` structure, for instance
```bash
nohup python src/simulator/simulator.py &
```

This command starts a background Python process running the simulation. It is recommended to leave this process running at least for a couple of days (for parameters of the order used in the paper).

The `simulator/` directory contains two important directories: The `task-sets` directory contains all the task tuples $(S, Q)$ generated - each line in the CSV files contain characteristics (runtimes, no. of processors, submit time) of a job. The `training-data` directory contains all of the trial score distributions generated - each line in the CSV files represents the observed scheduling behavior of a job (characteristics + score).

The `Simulator` class have two methods to manage the generated files. `clear_files()` can be used to clear the generated data (warning: this method deletes all generated files). `gather_training_data()` on the other hand, join all the trial score into one file. Modify any parameter to suit you needs.

If the workload used changes, it will be necessary to change the files `deployment_cluster.xml` and `simple_cluster.xml` (check your workload no. of processors).

### Regressor
The regressor module is the simplest amoung the others. To execute the code is enough to run
```bash
python /src/regressor/regressor.py
```

The parameters are also defined as variables on the top of the script. The functions (our polynomials) are defined at `polynomials.py`. This module can be flexible to newer functions as long as you follow our functions structure.

### Tester
Our last module is the tester. It is used to evaluate the regression-obtained heuristics as scheduling policies. To use it, edit the `workload_experiments()` function inputs at the end of the script. The avaliable options are the dictionaries `traces`, `simulators`, and `policies_flags` keys. Then, to run the module execute
```bash
python /src/tester/tester.py
```

Modifying the module for new functions/parameters may not be trivial at the moment. You need to manually add your functions/parameters on the `.c` and `.h` files and recompile it. 

## Reproduce our results
To reproduce our results use the following parameters. Your results may differ on RNG-dependent parts of our code (generating tuples, etc.).

**Simulator**:
```python
SIMULATION_PARAMETERS = {
    "workload": str(DATA_DIR / "workloads" / "lublin_256.swf"),
    "application": str(DATA_DIR / "applications" / "deployment_cluster.xml"),
    "platform": str(DATA_DIR / "platforms" / "simple_cluster.xml"),
    "number-of-tuples": 441, # Approximated
    "number-of-trials": 256_000,
    "size-of-S": 16,
    "size-of-Q": 32,
}
```

**Regressor**:
```python
SCORE_DISTRIBUTION = DATA_DIR / "scores" / "lublin-256-final-score.csv"
REPORT_FILE = DATA_DIR / "regression_report.json"
FUNCTIONS = [lin, qdr, cub, qua, qui, sex]
```

# Contact
Lucas de Sousa Rosa - roses.lucas@usp.br or roses.lucas404@gmail.com

# Acknowledgments
This research was supported by the EuroHPC EU Regale project (g.a. 956560), São Paulo Research Foundation (FAPESP, grants 19/26702-8 and 22/06906-0), and the MIAI Grenoble-Alpes institute (ANR project number 19-P3IA-0003).
