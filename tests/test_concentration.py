from adepoplan_backend import concentration
import io
import yaml


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
            count_file="count_fname", cell_area=100,
        )
        buf.seek(0)
        result = yaml.safe_load(buf)
        assert isinstance(result, dict)
