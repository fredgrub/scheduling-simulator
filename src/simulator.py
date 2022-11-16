import os
import numpy as np
import shutil
import subprocess
import argparse
from random import seed, randint
from swf_reader import ReaderSWF

class Simulator:

    _jobs_S = None
    _jobs_Q = None
    _current_file = "current-simulation.csv"
    _result_file = "result-temp.dat"
    _task_sets_path = "task-sets/"
    _states_path = "states/"
    _training_data_path = "training-data/"
    _permutation_indexes = None

    def __init__(self, workload, deployment, cluster, number_of_tuples, number_of_trials, size_of_S, size_of_Q, fixed_seed):
        self.workload = workload
        self.deployment = deployment
        self.cluster = cluster
        
        self.number_of_tuples = number_of_tuples
        self.number_of_trials = number_of_trials
        self.size_of_S = size_of_S
        self.size_of_Q = size_of_Q
        self.tuple_size = size_of_S + size_of_Q

        self.number_of_jobs = None
        self.number_of_nodes = None
        self.model_jobs = None
        self.get_workload_info()

        if fixed_seed:
            seed(42)

    def get_workload_info(self):
        reader = ReaderSWF(self.workload)
        self.model_jobs = reader.jobs_info
        self.number_of_jobs = reader.number_of_jobs
        self.number_of_nodes = reader.number_of_nodes

    def get_start_index(self):
        start = 0
        while os.path.exists("training-data/set-" + str(start) + ".csv") == True:
            start = start + 1
        return start

    def get_task_sets_file(self, index):
        return "task-sets/set-" + str(index) + ".csv"
    
    def get_states_file(self, index):
        return "states/set-" + str(index) + ".csv"
    
    def get_training_data_file(self, index):
        return "training-data/set-" + str(index) + ".csv"

    def get_random_index(self):
        maximum_start_index = (self.number_of_jobs - 1) - (self.tuple_size)
        return randint(0, maximum_start_index)

    def store_tuple(self, index):
        with open(self.get_task_sets_file(index), "w+") as current_tuple:
            rng_index = self.get_random_index()

            earliest_submit = self.model_jobs['r'][rng_index]

            for i in range(self.size_of_S):
                self._jobs_S['p'].append(self.model_jobs['p'][rng_index + i])
                self._jobs_S['q'].append(self.model_jobs['q'][rng_index + i])
                self._jobs_S['r'].append(self.model_jobs['r'][rng_index + i] - earliest_submit)

                current_tuple.write(str(self._jobs_S['p'][i])+","+str(self._jobs_S['q'][i])+","+str(self._jobs_S['r'][i])+"\n")
            for i in range(self.size_of_Q):
                self._jobs_Q['p'].append(self.model_jobs['p'][rng_index + i])
                self._jobs_Q['q'].append(self.model_jobs['q'][rng_index + i])
                self._jobs_Q['r'].append(self.model_jobs['r'][rng_index + i] - earliest_submit)
                
                current_tuple.write(str(self._jobs_Q['p'][i])+","+str(self._jobs_Q['q'][i])+","+str(self._jobs_Q['r'][i])+"\n")

    def create_initial_state(self, index):
        shutil.copyfile(self.get_task_sets_file(index), self._current_file)
        subprocess.call([f"./trials_simulator {self.cluster} {self.deployment} -state > {self.get_states_file(index)}"], shell=True)

    def clear_possible_artifacts(self, index):
        if os.path.isfile(self._result_file):
            os.remove(self._result_file)
        if os.path.isfile(self.get_training_data_file(index)):
            os.remove(self.get_training_data_file(index))

    def initialize_permutation_indexes(self):
        self._permutation_indexes = np.empty(shape=(self.number_of_trials, self.size_of_Q), dtype=int)
        for j in range(0, self.number_of_trials):
            self._permutation_indexes[j] = np.arange(self.size_of_Q)

    def create_permutation(self, index, shuffled_Q):        
        with open(self._current_file, "w+") as iteration_file:
            for k in range(self.size_of_Q):
                choose = randint(0, self.size_of_Q - 1)
                buffer_runtimes = shuffled_Q['p'][choose]
                buffer_nodes = shuffled_Q['q'][choose] 
                buffer_submit = shuffled_Q['r'][choose]     
                shuffled_Q['p'][choose] = shuffled_Q['p'][k]
                shuffled_Q['q'][choose] = shuffled_Q['q'][k]
                shuffled_Q['r'][choose] = shuffled_Q['r'][k]
                shuffled_Q['p'][k] = buffer_runtimes
                shuffled_Q['q'][k] = buffer_nodes 
                shuffled_Q['r'][k] = buffer_submit      
                buffer_index = self._permutation_indexes[index, choose]
                self._permutation_indexes[index, choose] = self._permutation_indexes[index, k]
                self._permutation_indexes[index, k] = buffer_index;

            for j in range(self.size_of_S):
                iteration_file.write(f"{self._jobs_S['p'][j]},{self._jobs_S['q'][j]},{self._jobs_S['r'][j]}\n")
            for k in range(self.size_of_Q):
                iteration_file.write(f"{self._jobs_Q['p'][self._permutation_indexes[index, k]]},{self._jobs_Q['q'][self._permutation_indexes[index, k]]},{self._jobs_Q['r'][self._permutation_indexes[index, k]]}\n")

        return shuffled_Q

    def create_shuffled_Q(self):
        shuffled_Q = {'p': [], 'q': [], 'r': []}

        shuffled_Q['p'] = np.copy(self._jobs_Q['p'])
        shuffled_Q['q'] = np.copy(self._jobs_Q['q'])
        shuffled_Q['r'] = np.copy(self._jobs_Q['r'])

        return shuffled_Q

    def schedule_trials(self):

        shuffled_Q = self.create_shuffled_Q()

        for trial_index in range(self.number_of_trials):
            shuffled_Q = self.create_permutation(trial_index, shuffled_Q)
            subprocess.call([f"./trials_simulator {self.cluster} {self.deployment} >> {self._result_file}"], shell=True)

    def compute_AVGbsld(self, index):
        exp_sum_slowdowns = 0.0
        distribution = np.zeros(self.size_of_Q)
        exp_first_choice = np.zeros((self.number_of_trials), dtype=np.int32)
        exp_slowdowns = np.zeros((self.number_of_trials))

        for trialID in range(self.number_of_trials):
            exp_first_choice[trialID] = self._permutation_indexes[trialID, 0] #asserted
        
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
            output += f"{int(self._jobs_Q['p'][k])},{int(self._jobs_Q['q'][k])},{int(self._jobs_Q['r'][k])},{score_dist[k]}\n"
        
        with open(self.get_training_data_file(index), "w+") as output_file:
            output_file.write(output)

    def simulate(self):
        for tuple_index in range(self.get_start_index(), self.number_of_tuples):
            
            self._jobs_S = {'p': [], 'q': [], 'r': []}
            self._jobs_Q = {'p': [], 'q': [], 'r': []}

            self.store_tuple(tuple_index)
            self.create_initial_state(tuple_index)
            self.clear_possible_artifacts(tuple_index)
            self.initialize_permutation_indexes()
            self.schedule_trials()
            score_dist = self.compute_AVGbsld(tuple_index)
            self.save_score_distribution(tuple_index, score_dist)

    @staticmethod
    def delete_csv_files_from(directory):
        for file in os.listdir(directory):
            if file.endswith(".csv"):
                os.remove(os.path.join(directory, file))

    @classmethod
    def clear_files(cls):
        if os.path.isfile(cls._result_file):
            os.remove(cls._result_file)
        if os.path.isfile(cls._current_file):
            os.remove(cls._current_file)
        
        cls.delete_csv_files_from(cls._training_data_path)
        cls.delete_csv_files_from(cls._states_path)
        cls.delete_csv_files_from(cls._task_sets_path)

def main():

    parser = argparse.ArgumentParser(prog="Simulator", fromfile_prefix_chars="@", allow_abbrev=False)

    parser.add_argument('workload_file', type=str, nargs='?', help='Workload file (swf)')
    parser.add_argument('deployment_file', type=str, nargs='?', help='Application deployment file (xml)')
    parser.add_argument('platform_file', type=str, nargs='?', help='Simulation settings file (xml)')

    parser.add_argument('number_of_tuples', type=int, nargs='?', help='Number of (S,Q) tuples to simulate')
    parser.add_argument('number_of_trials', type=int, nargs='?', help='Number of permutations of Q')
    parser.add_argument('size_of_S', type=int, nargs='?', help='Number of jobs in set S')
    parser.add_argument('size_of_Q', type=int, nargs='?', help='Number of jobs in set Q')

    parser.add_argument('--fixed-seed', action='store_true', help='Fix a seed for the RNG')
    parser.add_argument('--clear', action='store_true', help='Clear simulation files')

    args = parser.parse_args()

    if not args.clear:
        simulator = Simulator(
            args.workload_file, args.deployment_file, args.platform_file, 
            args.number_of_tuples, args.number_of_trials, 
            args.size_of_S, args.size_of_Q, 
            args.fixed_seed)
            
        simulator.simulate()
    else:
        Simulator.clear_files()

if __name__ == "__main__":
    main()