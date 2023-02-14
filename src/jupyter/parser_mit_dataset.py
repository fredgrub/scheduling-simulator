import pandas as pd

def to_swf(mit_raw):
    """
    Convert the MIT dataset to SWF format. The raw dataset is the unique parameter.
    """

    swf_fields = [
        "Job number", 
        "Submit time", 
        "Wait time", 
        "Run time", 
        "Number of allocated processors", 
        "Average CPU time used", 
        "Used memory", 
        "Requested number of processors", 
        "Requested time", 
        "Requested memory", 
        "Status", 
        "User ID", 
        "Group ID", 
        "Executable (application) number", 
        "Queue number", 
        "Partition number", 
        "Preceding job number", 
        "Think time from preceding job"
    ]

    ignoreable_fields = [
        "Average CPU time used",
        "Used memory",
        "Status",
        "Group ID",
        "Executable (application) number",
        "Queue number",
        "Partition number",
        "Preceding job number",
        "Think time from preceding job"
    ]

    # Filter out jobs that runned on Xeon-P8 partition and completed successfully
    mit_raw = mit_raw[(mit_raw['partition'] == 'xeon-p8') & mit_raw['exit_code'] == 0]
    # mit_raw = mit_raw[mit_raw['partition'] == 'xeon-p8']
    mit_swf = pd.DataFrame(columns=swf_fields)

    # Convert the equivalent fields
    mit_swf['Submit time'] = mit_raw['time_submit']
    mit_swf['Wait time'] = mit_raw['time_start'] - mit_raw['time_submit']
    mit_swf['Run time'] = mit_raw['time_end'] - mit_raw['time_start']
    mit_swf['Requested time'] = mit_raw['timelimit']
    mit_swf['Requested number of processors'] = mit_raw['cpus_req']
    mit_swf['Number of allocated processors'] = mit_raw['cpus_req']
    mit_swf['Requested memory'] = mit_raw['mem_req']
    mit_swf['User ID'] = mit_raw['id_user']

    # sort the data by the "Submit time" column in ascending order
    mit_swf = mit_swf.sort_values("Submit time")

    # subtract the first value in the "Submit time" column from all other values
    mit_swf["Submit time"] = mit_swf["Submit time"] - mit_swf["Submit time"].iloc[0]

    mit_swf.reset_index(inplace=True, drop=True)
    mit_swf['Job number'] = mit_swf.index

    mit_swf[ignoreable_fields] = -1

    return mit_swf

def header_comments():
    return """\
; Version: 2.0
; Computer: MIT Supercloud TX-Gaia cluster
; Installation: MIT Supercloud - Massachusetts Institute of Technology
; Acknowledge: MIT Supercloud
; Information: https://dcc.mit.edu/data
; Conversion: Lucas de Sousa Rosa (roses.lucas@usp.br) Feb 8, 2023
; MaxJobs: 230830
; MaxRecords: 230830
; Preemption: No
; UnixStartTime: UNKNOWN
; TimeZoneString: UNKNOWN
; StartTime: UNKNOWN
; EndTime:   UNKNOWN
; MaxNodes: 480
; MaxProcs: 23040
; Note: Scheduler is Slurm (https://slurm.schedmd.com/).
;       This is a pseudo conversion of the MIT Supercloud logs (not every field is in standard format).
;       Filtered by partition 'xeon-p8' (CPU-only) and 'exit_code' 0.
;       There is an unusual 'Requested time', I believe it is some default value.
;       The 'Number of Allocated Processors' was not available. To facilitate the execution of the experiments, 
;       I considered this value equal to the 'Requested Number of Processors'.
"""

if __name__ == '__main__':
    mit_raw_file = 'mit-logs.csv'
    mit_swf_file = 'mit-supercloud.swf'

    mit_raw = pd.read_csv(mit_raw_file)
    mit_swf = to_swf(mit_raw)

    with open(mit_swf_file, 'w') as f:
        f.write(header_comments())
        mit_swf.to_csv(f, sep=' ', index=False, header=False)

