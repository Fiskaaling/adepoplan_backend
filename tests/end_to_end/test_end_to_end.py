import adepoplan_backend
import pytest
from pathlib import Path
import shutil


@pytest.fixture(scope='module', params=['ex1'])
def outdir(request, tmp_path_factory):
    """
    Run the given example in a temporary directory and return the output dir

    :param request: Input parameter object, provided by pytest
    :param tmp_path_factory: Temporary directory, provided by pytest
    :return: A directory containing both input and output files
    """

    # Copy all files to temporary directory
    example_dir = Path(__file__).parent / request.param
    tmp_path = tmp_path_factory.mktemp(example_dir.name)
    simdir = shutil.copytree(example_dir, tmp_path, dirs_exist_ok=True)

    # Run simulation from temporary directory
    adepoplan_backend.main(simdir / 'adepoplan.json')

    yield simdir


@pytest.mark.end_to_end
def test_contains_report(outdir):
    assert (outdir / 'report.html').exists()
