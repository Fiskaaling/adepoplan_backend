from adepoplan_backend import release


class Test_get_makrel_config_text:
    def test_returns_valid_yaml_text(self):
        txt = release.get_makrel_config_text(
            start_time='2022-01-01',
            stop_time='2022-01-02',
            makrel_area_file='test.geojson',
            min_release_depth=5,
            max_release_depth=10,
            sinkvel_knots=[1, 2, 3],
            sinkvel_cdf=[.0, .1, 1.0],
            num_particles=100,
        )

        import yaml
        import io
        buf = io.StringIO(txt)
        conf = yaml.safe_load(buf)
        assert isinstance(conf, dict)
