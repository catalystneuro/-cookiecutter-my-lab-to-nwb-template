"""Primary script to run to convert all sessions in a dataset using session_to_nwb."""
from pathlib import Path
from typing import Union
from concurrent.futures import ProcessPoolExecutor, as_completed
from pprint import pformat
import traceback
from tqdm import tqdm

from .{{cookiecutter.conversion_name}}_convert_session import session_to_nwb


def dataset_to_nwb(
    *,
    data_dir_path: Union[str, Path],
    output_dir_path: Union[str, Path],
    max_workers: int = 1,
    stub_test: bool = False,
    verbose: bool = True,
):
    """Convert the entire dataset to NWB.

    Parameters
    ----------
    data_dir_path : Union[str, Path]
        The path to the directory containing the raw data.
    output_dir_path : Union[str, Path]
        The path to the directory where the NWB files will be saved.
    max_workers : int, optional
        The number of workers to use for parallel processing, by default 1
    stub_test : bool, optional
        Whether to run a stub test, by default False
    verbose : bool, optional
        Whether to print verbose output, by default True
    """
    data_dir_path = Path(data_dir_path)
    session_to_nwb_kwargs_per_session = get_session_to_nwb_kwargs_per_session(
        data_dir_path=data_dir_path,
        output_dir_path=output_dir_path,
        stub_test=stub_test,
        verbose=verbose,
    )

    futures = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for session_to_nwb_kwargs in session_to_nwb_kwargs_per_session:
            exception_file_path = data_dir_path / f"ERROR_<nwbfile_name>.txt" # Add error file path here
            futures.append(
                executor.submit(
                    safe_session_to_nwb,
                    session_to_nwb_kwargs=session_to_nwb_kwargs,
                    exception_file_path=exception_file_path,
                )
            )
        for _ in tqdm(as_completed(futures), total=len(futures)):
            pass


def safe_session_to_nwb(*, session_to_nwb_kwargs: dict, exception_file_path: Union[Path, str]):
    """Convert a session to NWB while handling any errors by recording error messages to the exception_file_path.

    Parameters
    ----------
    session_to_nwb_kwargs : dict
        The arguments for session_to_nwb.
    exception_file_path : Path
        The path to the file where the exception messages will be saved.
    """
    exception_file_path = Path(exception_file_path)
    try:
        session_to_nwb(**session_to_nwb_kwargs)
    except Exception as e:
        with open(exception_file_path, mode="w") as f:
            f.write(f"session_to_nwb_kwargs: \n {pformat(session_to_nwb_kwargs)}\n\n")
            f.write(traceback.format_exc())


def get_session_to_nwb_kwargs_per_session(
    *,
    data_dir_path: Union[str, Path],
    output_dir_path: Union[str, Path],
    stub_test: bool = False,
    verbose: bool = True,
):
    """Get the kwargs for session_to_nwb for each session in the dataset.

    Parameters
    ----------
    data_dir_path : Union[str, Path]
        The path to the directory containing the raw data.
    output_dir_path : Union[str, Path]
        The path to the directory where the NWB files will be saved.
    stub_test : bool, optional
        Whether to run a stub test, by default False
    verbose : bool, optional
        Whether to print verbose output, by default True

    Returns
    -------
    list[dict[str, Any]]
        A list of dictionaries containing the kwargs for session_to_nwb for each session.
    """
    raise NotImplementedError # Implement this function to return the kwargs for session_to_nwb for each session


if __name__ == "__main__":

    # Parameters for conversion
    data_dir_path = Path("/Directory/With/Raw/Formats/")
    output_dir_path = Path("~/conversion_nwb/")
    stub_test = False

    session_to_nwb(data_dir_path=data_dir_path,
                    output_dir_path=output_dir_path,
                    stub_test=stub_test,
                    )
