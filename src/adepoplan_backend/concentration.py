import numpy as np


def make_concentration(config):
    import ladim_aggregate
    import pandas as pd
    import yaml
    import xarray as xr

    # Step 1: Create weight file
    feed_file = config['root_dir'] / config['concentration']['feed_file']
    weight_file = config['root_dir'] / config['concentration']['weight_file']
    feed_df = pd.read_csv(feed_file, comment="#", dtype={'feed': np.float64})
    ladim_output_file = config['root_dir'] / config['particles']['file']
    with xr.open_dataset(ladim_output_file, decode_cf=False) as ladim_dset:
        weights_dset = create_weights(feed_df, ladim_dset)
        weights_dset.to_netcdf(weight_file)

    # Step 2: Compute filter max age
    ladim_input_file = config['root_dir'] / 'ladim.yaml'
    max_age = np.timedelta64(config['user_input']['max_age'], 's')
    with open(ladim_input_file, encoding='utf-8') as fp:
        output_freq = yaml.safe_load(fp)['output_variables']['outper']
    filter_max_age = max_age - np.timedelta64(output_freq[0], output_freq[1])
    filter_max_age_seconds = filter_max_age.astype('timedelta64[s]').astype('int64')

    # Step 3: Create concentration config file
    crecon_conc_fname = config['root_dir'] / config['concentration']['conf']
    conc_fname = config['root_dir'] / config['concentration']['conc_file']
    feed_factor = config['user_input']['feed_factor']
    weight_file = config['root_dir'] / config['concentration']['weight_file']
    with open(crecon_conc_fname, 'w', encoding='utf-8') as fp:
        create_config_file(
            stream=fp,
            outfile=conc_fname,
            ladim_file=ladim_output_file,
            feed_factor=feed_factor,
            weight_file=weight_file,
            cell_area=config['user_input']['cell_area'],
            latdiff=config['user_input']['latdiff'],
            londiff=config['user_input']['londiff'],
            max_age=filter_max_age_seconds,
        )

    # Step 4: Compute concentrations
    ladim_aggregate.main(str(crecon_conc_fname))


def create_weights(feed_df, ladim_dset):
    # Convert from long form to table form
    feed_dset_full = convert_feed_table_to_matrix_form(feed_df)

    # Restrict table to min and max particle dates
    feed_dset = restrict_feed_dset(
        feed_dset=feed_dset_full,
        min_time=ladim_dset['release_time'].min().values.item(),
        max_time=ladim_dset['release_time'].max().values.item(),
    )

    # Count number of particles, for each entry in feed matrix
    feed_dset['pcount'] = count_particles_per_cage_and_dates(
        ladim_dset=ladim_dset,
        poly_id=feed_dset['poly_id'].values,
        dates=feed_dset['release_time'].values,
    )

    # Compute feed per particle.
    # If the number of particles is zero, feed is divided by one, to avoid
    # not-a-number and infinity values. The last entry is of feed_dset[feed] is
    # initially zero, but is set to be equal to the second last entry.
    feed_dset['feed_per_particle'] = feed_dset['feed'] / np.maximum(feed_dset['pcount'], 1)
    feed_dset['feed_per_particle'][-1, :] = feed_dset['feed_per_particle'][-2, :]
    return feed_dset


def restrict_feed_dset(feed_dset, min_time, max_time):
    import xarray as xr

    # Abort if something wrong about the limits
    assert min_time < max_time
    assert min_time < feed_dset['release_time'][-1]
    assert max_time > feed_dset['release_time'][0]

    # Search for min and max time within release times
    all_times = feed_dset['release_time'].values
    min_time = np.clip(min_time, all_times[0], all_times[-1])
    max_time = np.clip(max_time, all_times[0], all_times[-1])
    idx_min = np.searchsorted(all_times, min_time, side='right') - 1
    idx_max = np.searchsorted(all_times, max_time, side='left') + 1

    # Cut the dataset to a subset of release times determined by previous search
    new_dset = feed_dset.isel(release_time=slice(idx_min, idx_max))

    # Use min_time and max_time as endpoints
    new_time = [min_time] + new_dset['release_time'].values[1:-1].tolist() + [max_time]
    new_dset['release_time'] = xr.Variable('release_time', new_time)

    # Compute feeding amounts for endpoints
    new_period_1, = np.diff(new_dset['release_time'][:2].values)
    new_period_2, = np.diff(new_dset['release_time'][-2:].values)
    old_period_1, = np.diff(feed_dset['release_time'][idx_min:idx_min+2])
    old_period_2, = np.diff(feed_dset['release_time'][idx_max-2:idx_max])
    scale_1 = new_period_1 / old_period_1
    scale_2 = new_period_2 / old_period_2
    new_dset['feed'] = new_dset['feed'].copy(deep=True)
    new_dset['feed'][0] *= scale_1
    if idx_min + 2 < idx_max:  # Skip if both endpoints share the same bin
        new_dset['feed'][-2] *= scale_2
    new_dset['feed'][-1] = 0

    return new_dset


def count_particles_per_cage_and_dates(ladim_dset, poly_id, dates):
    import ladim_aggregate
    import netCDF4 as nc
    import xarray as xr

    with nc.Dataset('count.nc', 'w', diskless=True) as count_dset:
        time_bins = list(dates)
        last_entry = np.diff(time_bins[-2:]) + time_bins[-1]
        time_bins += last_entry.tolist()
        conf = dict(
            bins=dict(release_time=time_bins, poly_id='group_by'),
            filter_particle="pid > -1",
            infile=ladim_dset,
            outfile=count_dset,
        )
        ladim_aggregate.run_conf(conf)
        return xr.DataArray(
            data=count_dset.variables['histogram'][:],
            coords=dict(poly_id=count_dset.variables['poly_id'][:]),
            dims=('release_time', 'poly_id'),
        ).sel(poly_id=poly_id)
        # TODO: filter geojson poly_id after production data by date 
        # got and error value not found in index if the geojson file 
        # has a poly_id that is not in the production_data after it 
        # has been filtered by .rls times


def convert_feed_table_to_matrix_form(feed_df):
    feed_df['release_time'] = feed_df['time'].values.astype('datetime64[s]').astype('int64')
    feed_df = feed_df[['release_time', 'poly_id', 'feed']].set_index(['release_time', 'poly_id'])
    feed_dset = feed_df.to_xarray()
    feed_dset['feed'] = feed_dset['feed'].fillna(0)
    return feed_dset


def create_config_file(
        stream, outfile, ladim_file, feed_factor, weight_file,
        cell_area, max_age, latdiff, londiff,
):
    import importlib.resources
    from . import templates
    resource_file = importlib.resources.files(templates).joinpath('crecon.yaml')
    txt_template = resource_file.read_text(encoding='utf-8')
    txt = txt_template.format(
        crecon_output_file=outfile,
        ladim_output_file=ladim_file,
        feed_factor=feed_factor,
        weight_file=weight_file,
        cell_area=cell_area,
        max_age=max_age,
        latdiff=latdiff,
        londiff=londiff,
    )
    stream.write(txt)
