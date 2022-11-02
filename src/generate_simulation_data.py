import argparse
import subprocess
import glob
import os
from scheduling_simulator import SchedulingSimulator

def main():

    parser = argparse.ArgumentParser(
                    prog = 'Scheduling Simulator',
                    description = 'Compute the score distribution for a given HPC platform simulation.',
                    epilog = 'For more details check D. Carastan-Santos and R. Y. de Camargo, "Obtaining Dynamic Scheduling Policies with Simulation and Machine Learning," SC17: International Conference for High Performance Computing, Networking, Storage and Analysis, 2017, pp. 1-13.')

    parser.add_argument('filename', nargs='?', type=str, help='workload file')
    parser.add_argument('s_size', nargs='?', type=int, help='state set size')
    parser.add_argument('q_size', nargs='?', type=int, help='queue set size')
    parser.add_argument('num_tuples', nargs='?', type=int, help='number of tuples (S,Q)')
    parser.add_argument('num_trials', nargs='?', type=int, help='number of trials')
    parser.add_argument('--seed', action='store', type=int, help='set a seed to the RNG')
    parser.add_argument('--clear', action='store_true', help='clear files generated from simulations')
    
    args = parser.parse_args()
    
    if args.clear:  
        if len(glob.glob("training-data/*.csv")) != 0:
            subprocess.call(['rm training-data/*.csv'], shell=True)
        if len(glob.glob("task-sets/*.csv")) != 0:
            subprocess.call(['rm task-sets/*.csv'], shell=True)
        if len(glob.glob("states/*.csv")) != 0:
            subprocess.call(['rm states/*.csv'], shell=True)
        
        if(os.path.exists("result-temp.dat") == True):
            subprocess.call(['rm result-temp.dat'], shell=True)
        if(os.path.exists("current-simulation.csv") == True):
            subprocess.call(['rm current-simulation.csv'], shell=True)

        exit()
    
    workload_file = args.filename
    number_of_tuples = args.num_tuples
    number_of_trials = args.num_trials
    state_size = args.s_size
    queue_size = args.q_size
    random_seed = args.seed

    simulator = SchedulingSimulator(workload_file, number_of_tuples, number_of_trials, state_size, queue_size, random_seed)
    simulator.simulate()
    
if __name__ == "__main__":
    main()