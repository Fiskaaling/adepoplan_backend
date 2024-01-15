import adepoplan_backend
import pytest
from pathlib import Path
import xarray as xr
import shutil
pytestmark = pytest.mark.end_to_end


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


def test_produces_expected_files(outdir):
    filenames = {p.name for p in outdir.glob('*.*')}
    assert filenames == {
        'adepoplan.json',
        'conc.nc',
        'count.nc',
        'crecon_conc.yaml',
        'crecon_count.yaml',
        'ladim.yaml',
        'out.nc',
        'particles.rls',
        'report.html',
        'roms_small.nc',
    }


def test_particle_output_file_is_valid_netcdf_file(outdir):
    fname = outdir / 'out.nc'
    with xr.open_dataset(fname) as dset:
        assert 'particle_instance' in dset.dims


def test_concentration_output_file_is_valid_netcdf_file(outdir):
    fname = outdir / 'conc.nc'
    xr.load_dataset(fname)
