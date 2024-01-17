from adepoplan_backend import concentration
import io
import yaml
import pandas as pd
import xarray as xr


class Test_create_crecon_file_for_particle_counting:
    def test_creates_valid_yaml_file(self):
        buf = io.StringIO()
        concentration.create_crecon_file_for_particle_counting(
            stream=buf,
            outfile='my_outfile.yaml',
            ladim_file='ladim_output.nc',
        )
        buf.seek(0)
        result = yaml.safe_load(buf)
        assert isinstance(result, dict)


class Test_create_crecon_file_for_concentration:
    def test_creates_valid_yaml_file(self):
        buf = io.StringIO()
        concentration.create_crecon_file_for_concentration(
            stream=buf, outfile="conc_fname", ladim_file="ladim_output_file",
            feed_factor=1.2, weight_file="weight_file",
            count_file="count_fname", cell_area=100, max_age=100,
        )
        buf.seek(0)
        result = yaml.safe_load(buf)
        assert isinstance(result, dict)


class Test_compute_feed_rate:
    def test_returns_kg_per_day_and_cage(self):
        feed_df = pd.DataFrame(dict(
            time=['1970-01', '1970-02', '1970-03', '1970-01', '1970-02'],
            cage_id=['A', 'A', 'A', 'B', 'B'],
            feed=[31, 28, 56, 310, 280],
            poly_id=[1001, 1001, 1001, 1002, 1002],
        ))
        result = concentration.compute_feed_rate(feed_df)
        assert result.name == 'rate'
        assert result.dims == ('release_time', 'poly_id')
        assert result['release_time'].values.tolist() == [0, 2678400, 5097600]
        assert result['poly_id'].values.tolist() == [1001, 1002]
        assert result.values.tolist() == [[1, 10], [1, 10], [2, 0]]
