import os
import sys
import pathlib
import numpy as np
import shutil
import subprocess
from scipy.stats import qmc
import argparse
from random import seed, randint, shuffle, random


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
    "population-size": 40,
    "mutation-prob": 0.05,
    "number-of-generations": 5,
    "size-of-S": 16,
    "size-of-Q": 32,
}
parser=argparse.ArgumentParser()
parser.add_argument("-l","--hypercube",help="random (default) or hypercube?",action="store_true")
args = parser.parse_args()


class Simulator:
    _jobs_S = None
    _jobs_Q = None
    _current_file = SIMULATION_DIR / "current-simulation.csv"
    _result_file = SIMULATION_DIR / "result-temp.dat"
    _gather_file = SIMULATION_DIR / "training-data.csv"
    _task_sets_path = SIMULATION_DIR / "task-sets"
    _states_path = SIMULATION_DIR / "states"
    _training_data_path = SIMULATION_DIR / "training-data"
    _global_training_data_path = SIMULATION_DIR / "training-data" / "global_training_data.csv"
    _global_training_data_path = SIMULATION_DIR / "training-data" / "global_training_data.csv"
    _permutation_indices = None
    _parents_indices = None
    _children_indices = None
    _current_generation = 0    

    def __init__(
        self, workload, deployment, cluster, number_of_tuples, population_size, number_of_generations, mutation_prob, size_of_S, size_of_Q, fixed_seed
    ):
        self.workload = workload
        self.deployment = deployment
        self.cluster = cluster

        self.number_of_tuples = number_of_tuples
        self.population_size = population_size
        self.population_size_with_children = 2 * self.population_size
        self.number_of_generations = number_of_generations
        self.mutation_prob = mutation_prob
        self.size_of_S = size_of_S
        self.size_of_Q = size_of_Q
        self.tuple_size = size_of_S + size_of_Q

        self.number_of_jobs = None
        self.number_of_processors = None
        self.model_jobs = None
        self.get_workload_info()
        self.global_data=open(self._global_training_data_path,"w+")

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
        #return
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

    
    def mutate_children(self):
        for children in self._children_indices:
            for j in range(self.size_of_Q - 1):
                rng = random()
                if rng <= self.mutation_prob:
                    swap = children[j + 1]
                    children[j + 1] = children[j]
                    children[j] = swap

    
    def crossover(self, _mother, _father, index):
        _son_heritage_father = []
        _daughter_heritage_mother = []
        _m = 0
        _f = 0
        _son = self._children_indices[index]
        _daughter = self._children_indices[(self.population_size // 2) + index]
        _crossover_point = randint(0, self.size_of_Q - 1)
        #print("Crossover point: ", _crossover_point)
        # get genes from father
        for i in range(0, self.size_of_Q):
            if i <= _crossover_point:
                # the son part
                _son[i] = _father[i]
                _son_heritage_father.append(_father[i])
                # the daughter part
                _daughter[i] = _mother[i]
                _daughter_heritage_mother.append(_mother[i])
            else:
                #the son part
                while _mother[_m] in _son_heritage_father:
                    _m = _m + 1
                _son[i] = _mother[_m]
                _m = _m + 1
                #the daughter part
                while _father[_f] in _daughter_heritage_mother:
                    _f = _f + 1
                _daughter[i] = _father[_f]
                _f = _f + 1       
        

    def create_childrens(self):
        self._children_indices = np.empty(shape=(self.population_size, self.size_of_Q), dtype=int)
        for i in range(self.population_size // 2):
            _father_index = randint(0, self.population_size - 1)
            _mother_index = randint(0, self.population_size - 1)
            while _father_index == _mother_index:
                _father_index = randint(0, self.population_size - 1)
            _father = self._parents_indices[_father_index]
            _mother = self._parents_indices[_mother_index]
            self.crossover(_mother, _father, i)
            self.mutate_children()
    
    def initialize_population_indexes(self): 
        #if self._current_generation == 0:  
        self._parents_indices = np.empty(shape=(self.population_size, self.size_of_Q), dtype=int)
       #print(self._parents_indices[0])
        if args.hypercube :
            sampler= qmc.LatinHypercube(d=self.size_of_Q)
            lhs=sampler.random(n=self.population_size)
            for indiv in range (0,self.population_size):
                prob = lhs[indiv]
                copy=[]
            
                
                for i in range ( 0,self.size_of_Q):
                    
                    idx=randint(0, self.size_of_Q - 1)
                    p=random()
                    
                    while (np.isin(idx,self._parents_indices[indiv]) or p>prob[i]) :
                        idx=randint(0, self.size_of_Q - 1)
                        p=random()
                    #print(np.isin(idx,self._parents_indices[indiv]))
                    self._parents_indices[indiv][i]=idx
                    copy.append(idx)
                    #print(copy.count(idx))
                print(self._parents_indices[indiv])


        else:     
            
            for j in range(0, self.population_size):                
                self._parents_indices[j] = np.arange(self.size_of_Q)
                
                shuffle(self._parents_indices[j])
                print(self._parents_indices[j])
            
        
        #else:
        #    self.create_childrens()


    def create_permutation(self, individual_indices, index,  shuffled_Q):
        with open(self._current_file, "w+") as iteration_file:
            for k in range(self.size_of_Q):
                #choose = randint(0, self.size_of_Q - 1)
                choose = individual_indices[k]
                #print(individual_indices)
                #print(choose)
                #return
                buffer_runtimes = shuffled_Q["p"][choose]
                buffer_nodes = shuffled_Q["q"][choose]
                buffer_submit = shuffled_Q["r"][choose]
                shuffled_Q["p"][choose] = shuffled_Q["p"][k]
                shuffled_Q["q"][choose] = shuffled_Q["q"][k]
                shuffled_Q["r"][choose] = shuffled_Q["r"][k]
                shuffled_Q["p"][k] = buffer_runtimes
                shuffled_Q["q"][k] = buffer_nodes
                shuffled_Q["r"][k] = buffer_submit
                #print(self._permutation_indices)
                #buffer_index = self._permutation_indices[index, choose]
                #self._permutation_indices[index, choose] = self._permutation_indices[index, k]
                #self._permutation_indices[index, k] = buffer_index

            for j in range(self.size_of_S):
                iteration_file.write(f"{self._jobs_S['p'][j]},{self._jobs_S['q'][j]},{self._jobs_S['r'][j]}\n")
            for k in range(self.size_of_Q):
                iteration_file.write(
                    f"{self._jobs_Q['p'][self._permutation_indices[index, k]]},{self._jobs_Q['q'][self._permutation_indices[index, k]]},{self._jobs_Q['r'][self._permutation_indices[index, k]]}\n"
                )

        return shuffled_Q

    def create_shuffled_Q(self):
        shuffled_Q = {"p": [], "q": [], "r": []}

        shuffled_Q["p"] = np.copy(self._jobs_Q["p"])
        shuffled_Q["q"] = np.copy(self._jobs_Q["q"])
        shuffled_Q["r"] = np.copy(self._jobs_Q["r"])

        return shuffled_Q

    def schedule_population(self):
        shuffled_Q = self.create_shuffled_Q()

        if self._result_file.exists():
                self._result_file.unlink()    

        for index, individual in enumerate(self.population_indices):
            shuffled_Q = self.create_permutation(individual, index , shuffled_Q)
            #print(shuffled_Q)
            #return            
            subprocess.run(
                ["./trials_simulator", self.cluster, self.deployment],
                stdout=open(self._result_file, "a+"),
                cwd=SIMULATION_DIR,
            )

    def save_score_distribution(self, index, score_dist):
        output = ""
        for k in range(self.size_of_Q):
            output += (
                f"{int(self._jobs_Q['p'][k])},{int(self._jobs_Q['q'][k])},{int(self._jobs_Q['r'][k])},{score_dist[k]}\n"
            )

        with open(self.get_training_data_file(index), "w+") as output_file:
            output_file.write(output)
        self.global_data.write(output)

    def select(self):
        with open(self._result_file, "r") as rf:
            lines = rf.readlines()
            arr_slowdowns = np.asarray([float(_str.rstrip("\n")) for _str in lines])
            #print(arr_lines)
            best_indvs = arr_slowdowns.argsort()[:self.population_size]
            #print(best_indvs)
            lst_next_indvs = []
            for indv in best_indvs:
                lst_next_indvs.append(self.population_indices[indv])
            #print(lst_next_indvs)
            self._parents_indices = np.asarray(lst_next_indvs)
            print("Bounded Slowdown: ", arr_slowdowns[best_indvs[0]])
            
    def define_score_dist(self):
        with open(self._result_file, "r") as rf:
            lines = rf.readlines()
            arr_slowdowns = np.asarray([float(_str.rstrip("\n")) for _str in lines])
            #print(arr_lines)
            best_indiv_idx = arr_slowdowns.argsort()[0]
            best_indiv=self.population_indices[best_indiv_idx]
            target_score=[0]*self.size_of_Q
            cpt=1
            for idx in best_indiv:
                target_score[idx]=cpt/self.size_of_Q
                cpt=cpt+1
            print(target_score)
            return target_score
    
    def simulate(self):
        for tuple_index in range(self.get_start_index(), self.number_of_tuples):
            self._jobs_S = {"p": [], "q": [], "r": []}
            self._jobs_Q = {"p": [], "q": [], "r": []}

            self.store_tuple(tuple_index)
            self.create_initial_state(tuple_index)
            self.clear_possible_artifacts(tuple_index)
            for gen in range(self.number_of_generations):
                print("Generation: ", gen)
                if gen == 0: 
                    self.initialize_population_indexes()                    
                    self.create_childrens()                    
                else:
                    self.create_childrens()                    
                #print("Parents: ", self._parents_indices)
                #print("Children: ", self._children_indices)
                #self.population_indices = self._parents_indices + self._children_indices
                self.population_indices = np.concatenate((self._parents_indices, self._children_indices))
                self._permutation_indices = self.population_indices                  
                #print(self.population_indices)
                self.schedule_population()
                self.select()
            #    score_dist = self.compute_AVGbsld(tuple_index)
                self._current_generation = gen
            score_dist=self.define_score_dist()
            self.save_score_distribution(tuple_index, score_dist)
            

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
    if args.hypercube:
        print("cc")
    simulator = Simulator(
        SIMULATION_PARAMETERS["workload"],
        SIMULATION_PARAMETERS["application"],
        SIMULATION_PARAMETERS["platform"],
        SIMULATION_PARAMETERS["number-of-tuples"],
        SIMULATION_PARAMETERS["population-size"],
        SIMULATION_PARAMETERS["number-of-generations"],
        SIMULATION_PARAMETERS["mutation-prob"],
        SIMULATION_PARAMETERS["size-of-S"],
        SIMULATION_PARAMETERS["size-of-Q"],
        True
    )
    


    simulator.simulate()
    # simulator.clear_files()
    # simulator.gather_training_data()
