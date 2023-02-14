import pandas as pd
import os

SWF_FIELDS = [
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

def header_comments(max_jobs):
    return f"""\
; Version: 2.0
; Computer: LANL Mustang Cluster
; Installation: Los Alamos National Lab (LANL)
; Acknowledge: ATLAS project
; Information: https://ftp.pdl.cmu.edu/pub/datasets/ATLAS/index.html
; Conversion: Lucas de Sousa Rosa (roses.lucas@usp.br) Feb 14, 2023
; MaxJobs: {max_jobs}
; MaxRecords: {max_jobs}
; Preemption: No
; TimeZoneString: America/Chicago
; MaxNodes: 1600
; MaxProcs: 38400
; Note: Scheduler is Slurm (https://slurm.schedmd.com/).
;       Filtered by job_status == COMPLETED, and jobs with `wallclock_limit` bigger than 960 minutes.
;       Also removed empty entries.
"""

if __name__ == '__main__':
    path_to_file = '../data/'
    dataset_file = 'mustang_release_v1.0beta.csv'
    workload_file = 'mustang_release_v1.0beta.swf'

    openable_file = os.path.join(path_to_file, dataset_file)
    writeable_file = os.path.join(path_to_file, workload_file)

    atlas_swf = pd.DataFrame(columns=SWF_FIELDS)

    for chunk in pd.read_csv(openable_file, chunksize=50000):       
        # Filter out jobs with missing information
        chunk = chunk.dropna(subset=['submit_time', 'start_time', 'end_time'])

        chunk['submit_time'] = pd.to_datetime(chunk['submit_time'], utc=True, format='%Y-%m-%d %H:%M:%S%z')
        chunk['start_time'] = pd.to_datetime(chunk['start_time'], utc=True, format='%Y-%m-%d %H:%M:%S%z')
        chunk['end_time'] = pd.to_datetime(chunk['end_time'], utc=True, format='%Y-%m-%d %H:%M:%S%z')
        chunk['wallclock_limit'] = pd.to_timedelta(chunk['wallclock_limit'])
        chunk['job_status'] = chunk['job_status'].astype('category')

        max_wallclock_limit = 57600 # 16 hours
        chunk = chunk[(chunk['job_status'] == "COMPLETED") & (chunk['wallclock_limit'].dt.total_seconds().astype('int64') <= max_wallclock_limit)]

        chunk_swf = pd.DataFrame(columns=SWF_FIELDS)

        number_of_cores_per_node = 24
        chunk_swf['Submit time'] = chunk['submit_time']
        chunk_swf['Wait time'] = chunk['start_time'] - chunk['submit_time']
        chunk_swf['Run time'] = chunk['end_time'] - chunk['start_time']
        chunk_swf['Number of allocated processors'] = chunk['node_count'] * number_of_cores_per_node
        chunk_swf['Requested number of processors'] = chunk['tasks_requested']
        chunk_swf['Requested time'] = chunk['wallclock_limit']
        chunk_swf['User ID'] = chunk['user_ID']
        chunk_swf['Group ID'] = chunk['group_ID']

        # Concatenate the `chunk_swf` to `atlas_swf`
        atlas_swf = pd.concat([atlas_swf, chunk_swf])

    irrelevant_fields = [
        "Average CPU time used",
        "Used memory",
        "Requested memory",
        "Status",
        "Executable (application) number",
        "Queue number",
        "Partition number",
        "Preceding job number",
        "Think time from preceding job"
    ]

    # Sort the dataframe by `Submit time` in ascending order
    atlas_swf = atlas_swf.sort_values(by='Submit time', ascending=True)

    # Subtract the first `Submit time` from all `Submit time`s
    atlas_swf['Submit time'] = atlas_swf['Submit time'] - atlas_swf['Submit time'].iloc[0]

    # Convert `Submit time` to seconds
    atlas_swf['Submit time'] = atlas_swf['Submit time'].dt.total_seconds().astype('int64')

    # Convert `Wait time`, `Run time` and `Requested time` to seconds
    atlas_swf['Wait time'] = atlas_swf['Wait time'].dt.total_seconds().astype('int64')
    atlas_swf['Run time'] = atlas_swf['Run time'].dt.total_seconds().astype('int64')
    atlas_swf['Requested time'] = atlas_swf['Requested time'].dt.total_seconds().astype('int64')

    # Reset the index and assign the index + 1 as the `Job number`
    atlas_swf = atlas_swf.reset_index(drop=True)
    atlas_swf['Job number'] = atlas_swf.index + 1

    atlas_swf[irrelevant_fields] = -1

    with open(writeable_file, 'w') as f:
        f.write(header_comments(len(atlas_swf)))
        atlas_swf.to_csv(f, sep=' ', index=False, header=False)