from adepoplan_backend import concentration
import io
import yaml


class Test_create_crecon_file_for_particle_counting:
    def test_creates_valid_yaml_file(self):
        buf = io.StringIO()
        concentration.create_crecon_file_for_particle_counting(buf)
        buf.seek(0)
        result = yaml.safe_load(buf)
        assert isinstance(result, dict)


class Test_create_crecon_file_for_concentration:
    def test_creates_valid_yaml_file(self):
        buf = io.StringIO()
        concentration.create_crecon_file_for_concentration(buf)
        buf.seek(0)
        result = yaml.safe_load(buf)
        assert isinstance(result, dict)
