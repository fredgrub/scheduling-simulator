import re

class ReaderSWF:
    def __init__(self, filename):
        self.filename = filename
        self.number_of_jobs = None
        self.number_of_nodes = None
        self.jobs_info = {'p': [], 'q': [], 'r': []}

    def read_and_extract_data(self):
        try:
            with open(self.filename, 'r') as reader:
                for line in reader.readlines():
                    
                    row = re.split(" +", line.lstrip(" "))
                    
                    if row[0] == ';':
                        if row[1] == "MaxJobs:":
                            self.number_of_jobs = int(row[2].rstrip())
                        elif row[1] == "MaxNodes:":
                            self.number_of_nodes = int(row[2].rstrip())
                        continue
                    
                    # row[4] is q, row[3] is p, and row[1] is r
                    if int(row[4]) > 0 and int(row[4]) <= 256 and int(row[3]) > 0:
                        self.jobs_info['p'].append(int(row[3]))
                        self.jobs_info['q'].append(int(row[4]))
                        self.jobs_info['r'].append(int(row[1]))
        except IOError:
            print("Problem while reading the file: " + self.filename)