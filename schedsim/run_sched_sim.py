import gdown
import json
import pathlib
import time
from fitsim.regressor import Regressor
from fitsim.polynomials import *
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich import print

DATA_DIR = pathlib.Path("data")


def check_and_download_data(module_name):
    """
    Check if the needed files exists. If not, download them.
    """
    with open(DATA_DIR / "downloadable_content.json") as f:
        data = json.load(f)

    # create the module directory if it doesn't exist
    module_dir = DATA_DIR / module_name
    if not module_dir.exists():
        module_dir.mkdir()

    for file_metadata in data[module_name]:
        file_id = file_metadata["file-id"]
        file_to_download = file_metadata["filename"]

        if not (module_dir / file_to_download).exists():
            print(f"[dim blue]Downloading {file_to_download}")
            gdown.download(
                id=file_id,
                output=str(module_dir / file_to_download),
                quiet=True,
            )

    print("[bold green]Done![/bold green]")
    time.sleep(1)


def run_fitsim():
    """
    Run the fitsim module.
    """

    functions = {
        "linear": lin,
        "quadratic": qdr,
        "cubic": cub,
        "quartic": qua,
        "quintic": qui,
    }

    # Display the available functions
    print("[bold blue]Available functions:[/bold blue]")
    for i, poly in enumerate(functions):
        print(f"[bold blue]{i + 1}.[/bold blue] {poly}")

    func_input = Prompt.ask(
        "[bold blue]Which functions do you want to use?[/bold blue] "
        + "(separate with commas and no spaces)"
    )

    # Convert the input to a list of functions
    functions_selected = [functions[func] for func in func_input.split(",")]

    # Ask the user for the score file
    score_file = Prompt.ask(
        "[bold blue]Which score file do you want to use?[/bold blue] "
        + "(must be in the fitsim directory)"
    )
    exit()
    # TODO: rewrite the regressor class to use multiple functions
    regressor = Regressor(
        DATA_DIR / "fitsim" / score_file,
        functions_selected,
    )


if __name__ == "__main__":
    # Write an welcome message
    print("[bold green]Welcome to the Scheduling Simulator code![/bold green]")

    module = Prompt.ask(
        "Which module do you want to run?",
        choices=["proxysim", "fitsim", "schedsim"],
    )

    print(f"[yellow italic]Checking for data files for {module}...")
    check_and_download_data(module)

    if module == "proxysim":
        print("Not implemented yet!")
    elif module == "fitsim":
        run_fitsim()
    elif module == "schedsim":
        print("Not implemented yet!")

    # create a regressor object
    # regressor = Regressor(
    #     DATA_DIR / score_file,
    #     lin,
    # )

    # # perform the regression
    # file_to_save = DATA_DIR / "regression_results.json"
    # regressor.regression(file_to_save)
