import os
import sys
import pathlib
import subprocess
import pandas as pd

# Add the src directory to the path so we can import the tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from tools.swf_reader import *

# Predefined paths (enable the script to be run from anywhere in the project)
EXPERIMENTS_DIR = pathlib.Path(__file__).parent
DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data"

SECONDS_IN_A_DAY = 86400
SIM_NUM_DAYS = 15
STATE_SIZE = 16

traces = {
    "ANL": [DATA_DIR / "workloads" / "ANL-Intrepid-2009-1.swf", DATA_DIR / "applications" / "deployment_anl.xml", 15],
    "CTC-SP2": [
        DATA_DIR / "workloads" / "CTC-SP2-1996-3.1-cln.swf",
        DATA_DIR / "applications" / "deployment_ctcsp2.xml",
        22,
    ],
    "HPC2N": [
        DATA_DIR / "workloads" / "HPC2N-2002-2.2-cln.swf",
        DATA_DIR / "applications" / "deployment_hpc2n.xml",
        83,
    ],
    "SDSC-BLUE": [
        DATA_DIR / "workloads" / "SDSC-BLUE-2000-4.2-cln.swf",
        DATA_DIR / "applications" / "deployment_blue.xml",
        64,
    ],
    "SDSC-SP2": [
        DATA_DIR / "workloads" / "SDSC-SP2-1998-4.2-cln.swf",
        DATA_DIR / "applications" / "deployment_sdscsp2.xml",
        47,
    ],
    "CURIE": [
        DATA_DIR / "workloads" / "CEA-Curie-2011-2.1-cln.swf",
        DATA_DIR / "applications" / "deployment_curie.xml",
        15,
    ],
    "LUBLIN 256": [
        {
            "actual": DATA_DIR / "workloads" / "lublin_256.swf",
            "estimated": DATA_DIR / "workloads" / "lublin_256_est.swf",
        },
        DATA_DIR / "applications" / "deployment_day.xml",
        50,
    ],
    "LUBLIN 1024": [
        {
            "actual": DATA_DIR / "workloads" / "lublin_1024.swf",
            "estimated": DATA_DIR / "workloads" / "lublin_1024_est.swf",
        },
        DATA_DIR / "applications" / "deployment_day_1024.xml",
        50,
    ],
    "MUSTANG": [
        DATA_DIR / "workloads" / "mustang_release_v1.0beta.swf",
        DATA_DIR / "applications" / "deployment_mustang.xml",
        50,
    ],
    "KIT-FH2": [DATA_DIR / "workloads" / "KIT-FH2-2016-1.swf", DATA_DIR / "applications" / "deployment_kitfh2.xml", 50],
}

simulators = {
    "ACTUAL": "sched-simulator-runtime",
    "ESTIMATED": "sched-simulator-estimate-backfilling",
    "BACKFILLING": "sched-simulator-estimate-backfilling",
}

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
    "SEX": "-sex",
}


def workload_experiments(workloads, policies, sim_types):
    for workload_trace in workloads:
        for sim_type in sim_types:
            if workload_trace in ["LUBLIN 256", "LUBLIN 1024"]:
                workload_file = (
                    traces[workload_trace][0]["actual"]
                    if sim_type == "ACTUAL"
                    else traces[workload_trace][0]["estimated"]
                )
            else:
                workload_file = traces[workload_trace][0]

            deploy_file = traces[workload_trace][1]
            number_of_experiments = traces[workload_trace][2]

            if sim_type == "BACKFILLING":
                backfilling_flag = "-bf"
            else:
                backfilling_flag = ""

            number_of_policies = len(policies)

            workload_jobs = ReaderSWF(workload_file)

            print(
                f"Performing scheduling performance test for the workload trace {workload_trace}.\nConfiguration: {sim_type}"
            )

            # DataFrame to store all slowdowns from all experiments
            slowdowns = pd.DataFrame(columns=policies)

            choose = 0
            for exp in range(number_of_experiments):
                task_file = open(EXPERIMENTS_DIR / "initial-simulation-submit.csv", "w+")
                earliest_submit = workload_jobs.jobs_info["r"][choose]

                number_of_jobs = 0

                state_jobs = {"p": [], "~p": [], "q": [], "r": []}
                for idx in range(STATE_SIZE):
                    state_jobs["p"].append(workload_jobs.jobs_info["p"][choose + idx])
                    state_jobs["q"].append(workload_jobs.jobs_info["q"][choose + idx])
                    state_jobs["r"].append(workload_jobs.jobs_info["r"][choose + idx] - earliest_submit)

                    if sim_type != "ACTUAL":
                        state_jobs["~p"].append(workload_jobs.jobs_info["~p"][choose + idx])
                        task_file.write(
                            f"{state_jobs['p'][idx]},{state_jobs['q'][idx]},{state_jobs['r'][idx]},{state_jobs['~p'][idx]}\n"
                        )
                    else:
                        task_file.write(f"{state_jobs['p'][idx]},{state_jobs['q'][idx]},{state_jobs['r'][idx]}\n")

                    number_of_jobs += 1

                queue_jobs = {"p": [], "~p": [], "q": [], "r": []}
                idx = 0
                while (
                    workload_jobs.jobs_info["r"][choose + STATE_SIZE + idx] - earliest_submit
                ) <= SECONDS_IN_A_DAY * SIM_NUM_DAYS:
                    queue_jobs["p"].append(workload_jobs.jobs_info["p"][STATE_SIZE + choose + idx])
                    queue_jobs["q"].append(workload_jobs.jobs_info["q"][STATE_SIZE + choose + idx])
                    queue_jobs["r"].append(workload_jobs.jobs_info["r"][STATE_SIZE + choose + idx] - earliest_submit)

                    if sim_type != "ACTUAL":
                        queue_jobs["~p"].append(workload_jobs.jobs_info["~p"][STATE_SIZE + choose + idx])
                        task_file.write(
                            f"{queue_jobs['p'][idx]},{queue_jobs['q'][idx]},{queue_jobs['r'][idx]},{queue_jobs['~p'][idx]}\n"
                        )
                    else:
                        task_file.write(f"{queue_jobs['p'][idx]},{queue_jobs['q'][idx]},{queue_jobs['r'][idx]}\n")

                    idx += 1
                    number_of_jobs += 1

                task_file.close()
                choose += STATE_SIZE + idx

                print(f"Performing scheduling experiment {exp + 1}. Number of tasks={number_of_jobs}")

                _buffer = open(EXPERIMENTS_DIR / "plot-temp.dat", "w+")
                for policy in policies:
                    policy_flag = policies_flags[policy]
                    subprocess.run(
                        [
                            f"./{simulators[sim_type]}",
                            DATA_DIR / "platforms" / "plat_day.xml",
                            DATA_DIR / "applications" / deploy_file,
                            backfilling_flag,
                            policy_flag,
                            "-nt",
                            str(number_of_jobs),
                        ],
                        stdout=_buffer,
                        cwd=EXPERIMENTS_DIR,
                    )

                _buffer.close()

                temp_data = pd.DataFrame(columns=policies)

                _buffer = open(EXPERIMENTS_DIR / "plot-temp.dat", "r")
                lines = list(_buffer)
                for i, policy in enumerate(policies):
                    temp_data[policy] = [float(lines[i])]
                _buffer.close()

                slowdowns = pd.concat([slowdowns, temp_data], ignore_index=True)

            slowdowns.to_csv(
                EXPERIMENTS_DIR / f"{workload_trace}_{sim_type}_{number_of_experiments}_{number_of_policies}.csv",
                index=False,
            )


if __name__ == "__main__":
    workload_experiments(
        ["CTC-SP2", "SDSC-BLUE", "LUBLIN 256"],
        ["FCFS", "WFP3", "UNICEF", "SPT", "SAF", "F2", "LIN", "QDR", "CUB", "QUA", "QUI", "SEX"],
        ["ACTUAL", "ESTIMATED"],
    )
