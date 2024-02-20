import os
import sys
import pathlib
import numpy as np
import shutil
import subprocess
from random import seed, randint

# Add the src directory to the path so we can import the tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from tools.swf_reader import *

# Predefined paths (enable the script to be run from anywhere in the project)
SIMULATION_DIR = pathlib.Path(__file__).parent
DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data"

SIMULATION_PARAMETERS = {
    "workload": str(DATA_DIR / "workloads" / "lublin_256.swf"),
    "application": str(DATA_DIR / "applications" / "deployment_cluster.xml"),
    "platform": str(DATA_DIR / "platforms" / "simple_cluster.xml"),
    "number-of-tuples": 1,
    "number-of-trials": 256000,
    "size-of-S": 16,
    "size-of-Q": 32,
}


class Simulator:
    _jobs_S = None
    _jobs_Q = None
    _current_file = SIMULATION_DIR / "current-simulation.csv"
    _result_file = SIMULATION_DIR / "result-temp.dat"
    _gather_file = SIMULATION_DIR / "training-data.csv"
    _task_sets_path = SIMULATION_DIR / "task-sets"
    _states_path = SIMULATION_DIR / "states"
    _training_data_path = SIMULATION_DIR / "training-data"
    _permutation_indexes = None

    def __init__(
        self, workload, deployment, cluster, number_of_tuples, number_of_trials, size_of_S, size_of_Q, fixed_seed
    ):
        self.workload = workload
        self.deployment = deployment
        self.cluster = cluster

        self.number_of_tuples = number_of_tuples
        self.number_of_trials = number_of_trials
        self.size_of_S = size_of_S
        self.size_of_Q = size_of_Q
        self.tuple_size = size_of_S + size_of_Q

        self.number_of_jobs = None
        self.number_of_processors = None
        self.model_jobs = None
        self.get_workload_info()

        if fixed_seed:
            seed(42)

    def get_workload_info(self):
        reader = ReaderSWF(self.workload)
        self.model_jobs = reader.jobs_info
        self.number_of_jobs = reader.number_of_jobs
        self.number_of_processors = reader.number_of_processors

    def get_start_index(self):
        start = 0
        while (self._training_data_path / f"set-{start}.csv").exists():
            start += 1
        return start

    def get_task_sets_file(self, index):
        return self._task_sets_path / f"set-{index}.csv"

    def get_states_file(self, index):
        return self._states_path / f"set-{index}.csv"

    def get_training_data_file(self, index):
        return self._training_data_path / f"set-{index}.csv"

    def get_random_index(self):
        maximum_start_index = (self.number_of_jobs - 1) - (self.tuple_size)
        return randint(0, maximum_start_index)

    def store_tuple(self, index):
        with open(self.get_task_sets_file(index), "w+") as current_tuple:
            rng_index = self.get_random_index()

            earliest_submit = self.model_jobs["r"][rng_index]

            for i in range(self.size_of_S):
                self._jobs_S["p"].append(self.model_jobs["p"][rng_index + i])
                self._jobs_S["q"].append(self.model_jobs["q"][rng_index + i])
                self._jobs_S["r"].append(self.model_jobs["r"][rng_index + i] - earliest_submit)

                current_tuple.write(
                    str(self._jobs_S["p"][i]) + "," + str(self._jobs_S["q"][i]) + "," + str(self._jobs_S["r"][i]) + "\n"
                )
            for i in range(self.size_of_Q):
                self._jobs_Q["p"].append(self.model_jobs["p"][self.size_of_S + rng_index + i])
                self._jobs_Q["q"].append(self.model_jobs["q"][self.size_of_S + rng_index + i])
                self._jobs_Q["r"].append(self.model_jobs["r"][self.size_of_S + rng_index + i] - earliest_submit)

                current_tuple.write(
                    str(self._jobs_Q["p"][i]) + "," + str(self._jobs_Q["q"][i]) + "," + str(self._jobs_Q["r"][i]) + "\n"
                )

    def create_initial_state(self, index):
        shutil.copyfile(self.get_task_sets_file(index), self._current_file)
        subprocess.run(
            ["./trials_simulator", self.cluster, self.deployment, "-state"],
            stdout=open(self.get_states_file(index), "w+"),
            cwd=SIMULATION_DIR,
        )

    def clear_possible_artifacts(self, index):
        if self._result_file.exists():
            self._result_file.unlink()
        if self.get_training_data_file(index).exists():
            self.get_training_data_file(index).unlink()

    def initialize_permutation_indexes(self):
        self._permutation_indexes = np.empty(shape=(self.number_of_trials, self.size_of_Q), dtype=int)
        for j in range(0, self.number_of_trials):
            self._permutation_indexes[j] = np.arange(self.size_of_Q)

    def create_permutation(self, index, shuffled_Q):
        with open(self._current_file, "w+") as iteration_file:
            for k in range(self.size_of_Q):
                choose = randint(0, self.size_of_Q - 1)
                buffer_runtimes = shuffled_Q["p"][choose]
                buffer_nodes = shuffled_Q["q"][choose]
                buffer_submit = shuffled_Q["r"][choose]
                shuffled_Q["p"][choose] = shuffled_Q["p"][k]
                shuffled_Q["q"][choose] = shuffled_Q["q"][k]
                shuffled_Q["r"][choose] = shuffled_Q["r"][k]
                shuffled_Q["p"][k] = buffer_runtimes
                shuffled_Q["q"][k] = buffer_nodes
                shuffled_Q["r"][k] = buffer_submit
                buffer_index = self._permutation_indexes[index, choose]
                self._permutation_indexes[index, choose] = self._permutation_indexes[index, k]
                self._permutation_indexes[index, k] = buffer_index

            for j in range(self.size_of_S):
                iteration_file.write(f"{self._jobs_S['p'][j]},{self._jobs_S['q'][j]},{self._jobs_S['r'][j]}\n")
            for k in range(self.size_of_Q):
                iteration_file.write(
                    f"{self._jobs_Q['p'][self._permutation_indexes[index, k]]},{self._jobs_Q['q'][self._permutation_indexes[index, k]]},{self._jobs_Q['r'][self._permutation_indexes[index, k]]}\n"
                )

        return shuffled_Q

    def create_shuffled_Q(self):
        shuffled_Q = {"p": [], "q": [], "r": []}

        shuffled_Q["p"] = np.copy(self._jobs_Q["p"])
        shuffled_Q["q"] = np.copy(self._jobs_Q["q"])
        shuffled_Q["r"] = np.copy(self._jobs_Q["r"])

        return shuffled_Q

    def schedule_trials(self):
        shuffled_Q = self.create_shuffled_Q()

        for trial_index in range(self.number_of_trials):
            shuffled_Q = self.create_permutation(trial_index, shuffled_Q)
            subprocess.run(
                ["./trials_simulator", self.cluster, self.deployment],
                stdout=open(self._result_file, "a+"),
                cwd=SIMULATION_DIR,
            )
            print("Trial ", trial_index, " of ", self.number_of_trials, end="\r")

    def report_trials_results(self):
        with open(self._result_file, "r") as rf:
            lines = rf.readlines()
            arr_slowdowns = np.asarray([float(_str.rstrip("\n")) for _str in lines])
            #print(arr_lines)
            best_trial = arr_slowdowns.argsort()[:1]
            #print(best_indvs)
            #lst_next_indvs = []
            #for indv in best_indvs:
            #    lst_next_indvs.append(self.population_indices[indv])
            #print(lst_next_indvs)
            #self._parents_indices = np.asarray(lst_next_indvs)
            print("Bounded Slowdown: ", arr_slowdowns[best_trial[0]])

    def compute_AVGbsld(self, index):
        exp_sum_slowdowns = 0.0
        distribution = np.zeros(self.size_of_Q)
        exp_first_choice = np.zeros((self.number_of_trials), dtype=np.int32)
        exp_slowdowns = np.zeros((self.number_of_trials))

        for trialID in range(self.number_of_trials):
            exp_first_choice[trialID] = self._permutation_indexes[trialID, 0]  # asserted

        trialID = 0
        with open(self._result_file, "r") as rf:
            lines = rf.readlines()
            if len(lines) != self.number_of_trials:
                index = index - 1
            for line in lines:
                exp_slowdowns[trialID] = float(line)
                exp_sum_slowdowns += float(line)
                trialID = trialID + 1

        for trialID in range(self.number_of_trials):
            distribution[exp_first_choice[trialID]] += exp_slowdowns[trialID]

        for k in range(self.size_of_Q):
            distribution[k] = distribution[k] / exp_sum_slowdowns

        return distribution

    def save_score_distribution(self, index, score_dist):
        output = ""
        for k in range(self.size_of_Q):
            output += (
                f"{int(self._jobs_Q['p'][k])},{int(self._jobs_Q['q'][k])},{int(self._jobs_Q['r'][k])},{score_dist[k]}\n"
            )

        with open(self.get_training_data_file(index), "w+") as output_file:
            output_file.write(output)

    def simulate(self):
        for tuple_index in range(self.get_start_index(), self.number_of_tuples):
            self._jobs_S = {"p": [], "q": [], "r": []}
            self._jobs_Q = {"p": [], "q": [], "r": []}

            self.store_tuple(tuple_index)
            self.create_initial_state(tuple_index)
            self.clear_possible_artifacts(tuple_index)
            self.initialize_permutation_indexes()
            self.schedule_trials()
            self.report_trials_results()
            #score_dist = self.compute_AVGbsld(tuple_index)
            #self.save_score_distribution(tuple_index, score_dist)

    @classmethod
    def clear_files(cls):
        if cls._result_file.exists():
            cls._result_file.unlink()
        if cls._current_file.exists():
            cls._current_file.unlink()

        for path in [cls._training_data_path, cls._states_path, cls._task_sets_path]:
            for file in path.glob("*.csv"):
                file.unlink()

    @classmethod
    def gather_training_data(cls):
        with open(cls._gather_file, "w+") as out_file:
            start = 0
            while (SIMULATION_DIR / f"training-data/set-{start}.csv").exists():
                with open(SIMULATION_DIR / f"training-data/set-{start}.csv", "r") as sample_file:
                    out_file.write(sample_file.read())
                start = start + 1


if __name__ == "__main__":
    simulator = Simulator(
        SIMULATION_PARAMETERS["workload"],
        SIMULATION_PARAMETERS["application"],
        SIMULATION_PARAMETERS["platform"],
        SIMULATION_PARAMETERS["number-of-tuples"],
        SIMULATION_PARAMETERS["number-of-trials"],
        SIMULATION_PARAMETERS["size-of-S"],
        SIMULATION_PARAMETERS["size-of-Q"],
        True,
    )

    simulator.simulate()
    # simulator.clear_files()
    # simulator.gather_training_data()