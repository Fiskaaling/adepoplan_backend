import pytest

from adepoplan_backend import concentration
import io
import yaml
import pandas as pd
import xarray as xr
import numpy as np


class Test_create_config_file:
    def test_creates_valid_yaml_file(self):
        buf = io.StringIO()
        concentration.create_config_file(
            stream=buf, outfile="conc_fname", ladim_file="ladim_output_file",
            feed_factor=1.2, weight_file="weight_file",
            cell_area=100, max_age=100,
            latdiff=0.001, londiff=0.002,
        )
        buf.seek(0)
        result = yaml.safe_load(buf)
        assert isinstance(result, dict)


class Test_create_weights:
    @pytest.fixture()
    def feed_df(self):
        # For testing simplicity, the feed weight is negative for cage B
        # Also, weight is multiplied by 10 every month
        return pd.DataFrame(dict(
            time=['1970-01', '1970-02', '1970-03', '1970-01', '1970-02'],
            cage_id=['A', 'A', 'A', 'B', 'B'],
            feed=[10, 100, 1000, -10, -100],
            poly_id=[1001, 1001, 1001, 1004, 1004],
        ))

    @pytest.fixture()
    def ladim_dset(self):
        return xr.Dataset(
            coords=dict(time=[0, 3000000, 6000000]),
            data_vars=dict(
                release_time=xr.Variable('particle', [0, 3000000, 6000000, 0, 0]),
                poly_id=xr.Variable('particle', [1001, 1004, 1004, 1001, 1005]),
                particle_count=xr.Variable('time', [1, 2, 5]),
                pid=xr.Variable('particle_instance', [0, 0, 1, 0, 1, 2, 3, 4]),
            ),
        )

    def test_has_the_same_coords_as_feed_table(self, feed_df, ladim_dset):
        result = concentration.create_weights(feed_df, ladim_dset)

        # Has the same coords as the feed table
        posix_time = feed_df['release_time'].values.astype('datetime64[s]').astype('int64')
        assert result['release_time'].values.tolist() == np.unique(posix_time).tolist()
        assert result['poly_id'].values.tolist() == np.unique(feed_df['poly_id']).tolist()

        # Returns correct particle counts
        assert result['pcount'].values.tolist() == [[2, 0], [0, 1], [0, 1]]

        # Returns correct feed matrix (restricted to the given time span)
        assert result['feed'].values.tolist() == [
            [10.0, -10.0],
            [100.0, -100.0],
            [0.0, 0.0]
        ]

        # Returns correct weight per particle
        # If there are zero particles, the feed is divided by 1 instead of 0.
        # The two last entries are equal.
        assert result['feed_per_particle'].values.tolist() == [
            [5, -10],
            [100, -100],
            [100, -100],
        ]


class Test_restrict_feed_dset:
    def test_returns_restricted_time(self):
        full = xr.Dataset(
            coords=dict(release_time=[10, 20, 30, 40, 50, 60], poly_id=[101]),
            data_vars=dict(
                feed=xr.Variable(
                    dims=('release_time', 'poly_id'),
                    data=np.array([[1., 2, 3, 4, 5, 6]]).T,
                )
            )
        )
        # Endpoints match exactly
        restricted = concentration.restrict_feed_dset(full, 20, 40)
        assert restricted.release_time.values.tolist() == [20, 30, 40]
        # Endpoints exceed dataset
        restricted = concentration.restrict_feed_dset(full, 0, 100)
        assert restricted.release_time.values.tolist() == [10, 20, 30, 40, 50, 60]
        # Partial endpoints
        restricted = concentration.restrict_feed_dset(full, 25, 42)
        assert restricted.release_time.values.tolist() == [25, 30, 40, 42]
        # Partial endpoints, single bin
        restricted = concentration.restrict_feed_dset(full, 22, 25)
        assert restricted.release_time.values.tolist() == [22, 25]

    def test_modifies_feed_value_at_endpoints(self):
        full = xr.Dataset(
            coords=dict(release_time=[4, 8, 12, 16, 20, 24], poly_id=[101]),
            data_vars=dict(
                feed=xr.Variable(
                    dims=('release_time', 'poly_id'),
                    data=np.array([[1., 2., 3., 4., 5., 6.]]).T,
                )
            )
        )
        # Endpoints match exactly
        restricted = concentration.restrict_feed_dset(full, 8, 20)
        assert restricted.feed.values.ravel().tolist() == [2, 3, 4, 0]
        # Endpoints exceed dataset
        restricted = concentration.restrict_feed_dset(full, 0, 100)
        assert restricted.feed.values.ravel().tolist() == [1, 2, 3, 4, 5, 0]
        # Partial endpoints
        restricted = concentration.restrict_feed_dset(full, 7, 22)
        assert restricted.feed.values.ravel().tolist() == [0.25, 2.0, 3.0, 4.0, 2.5, 0.0]
        # Partial endpoints, single bin
        restricted = concentration.restrict_feed_dset(full, 6, 7)
        assert restricted.feed.values.ravel().tolist() == [0.25, 0]
