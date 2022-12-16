import pandas as pd
from simulator.swf_reader import ReaderSWF

class Tester:

    _submission_file = "initial-simulation-submit.csv"
    _size_of_S = 16

    def __init__(self, workload_name, parameter_tag, policies_tag, number_of_experiments):
        self.workload_name = workload_name
        self.parameters_tag = parameter_tag
        self.policies_tag = policies_tag
        self.number_of_experiments = number_of_experiments

        self.number_of_jobs = None
        self.number_of_processors = None
        self.model_jobs = None
        self.get_workload_info()

        self.slowdowns = pd.DataFrame(columns=policies_tag)

        def get_workload_info(self):
            reader = ReaderSWF(self.workload_name)
            self.model_jobs = reader.jobs_info
            self.number_of_jobs = reader.number_of_jobs
            self.number_of_processors = reader.number_of_processors

        def seconds_in_fifteen_days():
            return 86400 * 15
        
        def run_tests(self):
            for _ in range(self.number_of_experiments):
                with open(self._submission_file, "w+") as f:
                    earliest_submit = self.model_jobs['r'][0]

                    # Collect S set
                    temp_S = {'p': [], '~p': [], 'q': [], 'r': []}
                    for i in range(self._size_of_S):
                        if self.parameter_tag in ["ESTIMATED", "BACKFILLING"]:
                            temp_S['~p'].append(self.model_jobs['~p'][i])
                        else:
                            temp_S['p'].append(self.model_jobs['p'][i])
                        
                        temp_S['q'].append(self.model_jobs['q'][i])
                        temp_S['r'].append(self.model_jobs['r'][i] - earliest_submit)

                        f.write("{},{},{}\n".format(temp_S['p'], temp_S['q'], temp_S['r']))
                    
                    temp_Q = {'p': [], 'q': [], 'r': []}
                    j = 0
                    while self.model_jobs['r'][self._size_of_S + j] - earliest_submit <= seconds_in_fifteen_days():

class TesterConfigs:

    policies_flags = {
        "FCFS": "",
        "WFP3": "-wfp3",
        "UNICEF": "-unicef",
        "SPT": "-spt",
        "SAF": "-saf",
        "F2": "-f2",
        "LIN": "-lin",
        "QDR": "-qdr",
        "CUB": "-cub",
        "QUA": "-qua",
        "QUI": "-qui",
        "SEX": "-sex"
        }

    workload_files = {
        "ANL": ["ANL-Intrepid-2009-1.swf", "deployment_anl.xml"],
        "CTC-SP2": ["CTC-SP2-1996-3.1-cln.swf", "deployment_ctcsp2.xml"],
        "HPC2N": ["HPC2N-2002-2.2-cln.swf", "deployment_hpc2n.xml"],
        "SDSC-BLUE": ["SDSC-BLUE-2000-4.2-cln.swf", "deployment_blue.xml"],
        "SDSC-SP2": ["SDSC-SP2-1998-4.2-cln.swf", "deployment_sdscsp2.xml"],
        "CURIE": ["CEA-Curie-2011-2.1-cln.swf", "deployment_curie.xml"],
        "LUBLIN 256": {
            "actual": ["lublin_256.swf", "deployment_day.xml"],
            "estimated": ["lublin_256_est.swf", "deployment_day.xml"]
            },
        "LUBLIN 1024": {
            "actual": ["lublin_1024.swf", "deployment_day_1024.xml"],
            "estimated": ["lublin_1024_est.swf", "deployment_day_1024.xml"]
            }
        }
    
    simulation_parameters = {
        "ACTUAL": ["sched-simulator-runtime", ""],
        "ESTIMATED": ["sched-simulator-estimate-backfilling", ""],
        "BACKFILLING": ["sched-simulator-estimate-backfilling", "-bf"]
    }

    def __init__(self, policies_tags, workloads_tags, states_tags):
        self.policies_labels = policies_tags
        self.workload_labels = workloads_tags
        self.states_labels = states_tags

    def get_workload_info(self):
        reader = ReaderSWF(self.workload)
        self.model_jobs = reader.jobs_info
        self.number_of_jobs = reader.number_of_jobs
        self.number_of_processors = reader.number_of_processors
        
    def build_command_stack(self, policies, workloads, states):
        # quero algo como ./sched-simulator-runtime xmls/plat_day.xml xmls/deployment_anl.xml -nt '+str(number_of_tasks)
        for workload in workloads:
            for state in states:
                for policy in policies:
                    tester = f"{self.simulation_parameters[state]}"
                    if workload == "LUBLIN 256" or workload == "LUBLIN 1024":
                        if state == "ACTUAL":
                            deployment = self.workload_files[workload]["actual"][1]
                        else:
                            deployment = self.workload_files[workload]["estimated"][1]
                    else:
                        deployment = self.workload_files[workload][1]

                    cmd = f"./{tester} xmls/plat_day.xml xmls/{deployment} {policy} -nt"


if __name__ == "__main__":
    policies = ["FCFS", "WFP3", "UNICEF", "SPT", "SAF", "F2", "LIN", "QDR", "CUB", "QUA", "QUI", "SEX"]
    workloads = ["LUBLIN 256", "CTC-SP2", "SDSC-BLUE"]
    states = ["ACTUAL", "ESTIMATED", "BACKFILLING"]

    tester = Tester(policies, workloads, states)
    tester.run_experiments()