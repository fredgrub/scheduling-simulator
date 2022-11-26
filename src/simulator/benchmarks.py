from simulator import Simulator

workload_file = "swfs/lubin_256.swf"
deployment_file = "deployment_cluster.xml"
platform_file = "simple_cluster.xml"
number_of_tuples = 1
number_of_trials = 100
size_of_S = 16
size_of_Q = 32
fixed_seed = True

simulator = Simulator(
    workload_file, deployment_file, platform_file, 
    number_of_tuples, number_of_trials,
    size_of_S, size_of_Q, fixed_seed)

simulator.simulate()
simulator.clear_files()