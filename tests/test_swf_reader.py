import pytest
import src.swf_reader as swf_reader

@pytest.mark.parametrize("workload_file, number_of_jobs, number_of_nodes", [
    ("src/swfs/ANL-Intrepid-2009-1.swf", 68936, 40960),
    ("src/swfs/CEA-Curie-2011-2.1-cln.swf", 773138, 5544),
    ("src/swfs/CTC-SP2-1996-3.1-cln.swf", 79302, 338),
    ("src/swfs/HPC2N-2002-2.2-cln.swf", 527371, 240),
    ("src/swfs/lublin_256.swf", 100000, 256),
    ("src/swfs/lublin_1024.swf", 100000, 1024),
    ("src/swfs/lublin_256_est.swf", 100000, 256),
    ("src/swfs/lublin_1024_est.swf", 100000, 1024),
    ("src/swfs/SDSC-BLUE-2000-4.2-cln.swf", 250440, 144),
    ("src/swfs/SDSC-SP2-1998-4.2-cln.swf", 73496, 128),
])
def test_read_swf(workload_file, number_of_jobs, number_of_nodes):
    reader = swf_reader.ReaderSWF(workload_file)
    reader.read_and_extract_data()
    
    assert reader.number_of_jobs == number_of_jobs
    assert reader.number_of_nodes == number_of_nodes