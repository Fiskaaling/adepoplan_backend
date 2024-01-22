from adepoplan_backend import particles


class Test_get_ladim_config_text:
    def test_returns_valid_yaml_text(self):
        txt = particles.get_ladim_config_text(
            start_time='2022-01-01',
            stop_time='2022-01-02',
            output_file='my_output_file.nc',
            max_age=200,
            out_freq=[1, "m"]
        )

        import yaml
        import io
        buf = io.StringIO(txt)
        conf = yaml.safe_load(buf)
        assert isinstance(conf, dict)
