import os
import random
import subprocess
import numpy as np
from swf_reader import ReaderSWF

class SchedulingSimulator:
    def __init__(self, workload_file, number_of_tuples, number_of_trials, state_size, queue_size, random_seed):
        if random_seed != None:
            random.seed(random_seed)
        self.number_of_tuples = number_of_tuples
        self.number_of_trials = number_of_trials
        self.state_size = state_size
        self.queue_size = queue_size
        self.tuple_size = state_size + queue_size

        self.number_of_jobs = None
        self.number_of_nodes = None
        self.workload_jobs = None
        self.get_workload_info(workload_file)

        self.start_index = None
        self.get_start_index()

    def get_workload_info(self, workload_file):
        reader = ReaderSWF(workload_file)
        self.workload_jobs = reader.jobs_info
        self.number_of_jobs = reader.number_of_jobs
        self.number_of_nodes = reader.number_of_nodes
    
    def get_start_index(self):
        start = 0
        while os.path.exists("training-data/set-"+str(start)+".csv") == True:
            start = start+1
        self.start_index = start

    def simulate(self):
        for tuple_index in range(self.start_index, self.number_of_tuples):
            
            state_jobs = {'p': [], 'q': [], 'r': []}
            queue_jobs = {'p': [], 'q': [], 'r': []}
            
            with open("task-sets/set-"+str(tuple_index)+".csv", "w+") as current_tuple:
                               
                maximum_start_index = (self.number_of_jobs - 1) - (self.tuple_size)
                random_index = random.randint(0, maximum_start_index)

                earliest_submit = self.workload_jobs['r'][random_index]

                for i in range(self.state_size):
                    state_jobs['p'].append(self.workload_jobs['p'][random_index + i])
                    state_jobs['q'].append(self.workload_jobs['q'][random_index + i])
                    state_jobs['r'].append(self.workload_jobs['r'][random_index + i] - earliest_submit)

                    current_tuple.write(str(state_jobs['p'][i])+","+str(state_jobs['q'][i])+","+str(state_jobs['r'][i])+"\n")
                for i in range(self.queue_size):
                    queue_jobs['p'].append(self.workload_jobs['p'][random_index + i])
                    queue_jobs['q'].append(self.workload_jobs['q'][random_index + i])
                    queue_jobs['r'].append(self.workload_jobs['r'][random_index + i] - earliest_submit)
                    
                    current_tuple.write(str(queue_jobs['p'][i])+","+str(queue_jobs['q'][i])+","+str(queue_jobs['r'][i])+"\n")

            subprocess.call(['cp task-sets/set-'+str(tuple_index)+'.csv' ' current-simulation.csv'], shell=True)  
            subprocess.call(['./trials_simulator simple_cluster.xml deployment_cluster.xml -state > states/set-'+str(tuple_index)+".csv"], shell=True)

            if(os.path.exists("result-temp.dat") == True):
                subprocess.call(['rm result-temp.dat'], shell=True)
            
            if(os.path.exists("training-data/set-"+str(tuple_index)+".csv") == True):
                subprocess.call(['rm training-data/set-'+str(tuple_index)+'.csv'], shell=True)
            
            permutation_indexes = np.empty(shape=(self.number_of_trials, self.queue_size), dtype=int)
            for j in range(0, self.number_of_trials):
                permutation_indexes[j] = np.arange(self.queue_size)

            shuffled_queue = {'p': [], 'q': [], 'r': []}

            shuffled_queue['p'] = np.copy(queue_jobs['p'])
            shuffled_queue['q'] = np.copy(queue_jobs['q'])
            shuffled_queue['r'] = np.copy(queue_jobs['r'])

            for trial_index in range(self.number_of_trials):
                with open("current-simulation.csv", "w+") as iteration_file:
                    for k in range(self.queue_size):
                        choose = random.randint(0, self.queue_size - 1)
                        buffer_runtimes = shuffled_queue['p'][choose]
                        buffer_nodes = shuffled_queue['q'][choose] 
                        buffer_submit = shuffled_queue['r'][choose]     
                        shuffled_queue['p'][choose] = shuffled_queue['p'][k]
                        shuffled_queue['q'][choose] = shuffled_queue['q'][k]
                        shuffled_queue['r'][choose] = shuffled_queue['r'][k]
                        shuffled_queue['p'][k] = buffer_runtimes
                        shuffled_queue['q'][k] = buffer_nodes 
                        shuffled_queue['r'][k] = buffer_submit      
                        buffer_index = permutation_indexes[trial_index, choose]
                        permutation_indexes[trial_index, choose] = permutation_indexes[trial_index, k]
                        permutation_indexes[trial_index, k] = buffer_index;

                    for k in range(self.state_size):
                        iteration_file.write(str(state_jobs['p'][k])+","+str(state_jobs['q'][k])+","+str(state_jobs['r'][k])+"\n")
                    for k in range(self.state_size):
                        iteration_file.write(str(queue_jobs['p'][permutation_indexes[trial_index, k]])+","+str(queue_jobs['q'][permutation_indexes[trial_index, k]])+","+str(queue_jobs['r'][permutation_indexes[trial_index, k]])+"\n")

                subprocess.call(['./trials_simulator simple_cluster.xml deployment_cluster.xml >> result-temp.dat'], shell=True)

            output = "" 
            exp_sum_slowdowns = 0.0
            distribution = np.zeros(self.queue_size)
            exp_first_choice = np.zeros((self.number_of_trials), dtype=np.int32)
            exp_slowdowns = np.zeros((self.number_of_trials))

            task_sets_prefix = "task-sets/set-"  
            results_prefix = "results/set"
            states_prefix = "states/set"

            for trialID in range(self.number_of_trials):
                exp_first_choice[trialID] = permutation_indexes[trialID, 0] #asserted

            trialID = 0
            with open("result-temp.dat", "r") as result_file:
                lines = result_file.readlines()
                if len(lines) != self.number_of_trials:
                    tuple_index = tuple_index - 1
                    continue
                for line in lines:
                    exp_slowdowns[trialID] = float(line)
                    exp_sum_slowdowns += float(line)    
                    trialID = trialID + 1

            for trialID in range(self.number_of_trials):
                distribution[exp_first_choice[trialID]] += exp_slowdowns[trialID]

            for k in range(self.queue_size):
                distribution[k] = distribution[k] / exp_sum_slowdowns

            for k in range(self.queue_size):
                output += str(int(queue_jobs['p'][k])) + "," + str(int(queue_jobs['q'][k])) + "," + str(int(queue_jobs['r'][k])) + ","
                output += str(distribution[k]) + "\n"
            

            with open("training-data/set-"+str(tuple_index)+".csv", "w+") as out_file:
                out_file.write(output)