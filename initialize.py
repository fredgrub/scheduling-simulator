# The pourpose of this script is to setup the necessary things to run the
# other scripts. It will create the necessary directories and files, and compile
# the necessary programs.
# Author: Lucas de Sousa Rosa <roses.lucas404 at gmail.com>
# Date: 2023-02-28

import os
import subprocess
import gdown


def download_from_google_drive():
    print("Downloading data...")

    #if not os.path.exists("data"):
        #gdown.download_folder(
        #    url="https://drive.google.com/drive/u/1/folders/1sFNmbXz3tTxjlvkFIGrQswVFU8fPsCeE",
       #     quiet=True,
      #      use_cookies=False,
     #   )
    #else:
    print("Data already downloaded!")


def compile_c_programs():
    print("Compiling C programs...")
    try:
        subprocess.run("make -s", shell=True, cwd="src/simulator/")
        subprocess.run("make -s", shell=True, cwd="src/tester/")
    except Exception as e:
        print("Error while compiling C programs:", e)
        exit(1)


if __name__ == "__main__":
    print("Initializing...")

    download_from_google_drive()
    compile_c_programs()

    print("Done!")
