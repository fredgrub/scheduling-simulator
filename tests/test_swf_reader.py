import pytest
import src.swf_reader as swf_reader

@pytest.mark.parametrize("workload_file, number_of_processors", [
    ("src/swfs/ANL-Intrepid-2009-1.swf", 163840),
    ("src/swfs/CEA-Curie-2011-2.1-cln.swf", 93312),
    ("src/swfs/CTC-SP2-1996-3.1-cln.swf", 338),
    ("src/swfs/HPC2N-2002-2.2-cln.swf", 240),
    ("src/swfs/lublin_256.swf", 256),
    ("src/swfs/lublin_1024.swf", 1024),
    ("src/swfs/lublin_256_est.swf", 256),
    ("src/swfs/lublin_1024_est.swf", 1024),
    ("src/swfs/SDSC-BLUE-2000-4.2-cln.swf", 1152),
    ("src/swfs/SDSC-SP2-1998-4.2-cln.swf", 128),
])
def test_read_swf(workload_file, number_of_processors):
    reader = swf_reader.ReaderSWF(workload_file)
    
    assert reader.number_of_processors == number_of_processors