import gdown
import json
import pathlib
import argparse

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
            gdown.download(
                id=file_id,
                output=str(module_dir / file_to_download),
                quiet=True,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--module",
        type=str,
        help="The module to run",
        choices=["schedsim", "fitsim", "expsim"],
        required=True,
    )
    args = parser.parse_args()

    selected_module = args.module

    check_and_download_data(selected_module)

    parameters = json.load(open(DATA_DIR / "parameters.json"))
    selected_parameters = parameters[selected_module]

    if selected_module == "schedsim":
        pass
    elif selected_module == "fitsim":
        import fitsim.regressor as rgr

        regressor = rgr.Regressor(
            DATA_DIR / selected_module / selected_parameters["score-file"],
            selected_parameters["functions"],
        )

        regressor.regression(
            DATA_DIR / selected_module / selected_parameters["report-file"]
        )

    elif selected_module == "expsim":
        pass
