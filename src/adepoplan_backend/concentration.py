def make_concentration(config):
    import ladim_aggregate
    import pandas as pd
    import yaml
    import numpy as np
    import xarray as xr

    # Step 1: Create weight file
    feed_file = config['root_dir'] / config['concentration']['feed_file']
    weight_file = config['root_dir'] / config['concentration']['weight_file']
    feed_df = pd.read_csv(feed_file)
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
    conc_fname = config['root_dir'] / config['concentration']['file']
    feed_factor = config['user_input']['feed_factor']
    weight_file = config['root_dir'] / config['concentration']['weight_file']
    with open(crecon_conc_fname, 'w', encoding='utf-8') as fp:
        create_crecon_file_for_concentration(
            stream=fp,
            outfile=conc_fname,
            ladim_file=ladim_output_file,
            feed_factor=feed_factor,
            weight_file=weight_file,
            cell_area=config['user_input']['cell_area'],
            latdiff=config['user_input']['latdiff'],
            londiff=config['user_input']['latdiff'],
            max_age=filter_max_age_seconds,
        )

    # Step 4: Compute concentrations
    ladim_aggregate.main(str(crecon_conc_fname))


def create_count(outfile, ladim_file):
    import ladim_aggregate
    conf = dict(
        bins=dict(poly_id='group_by', release_time=86400),
        filter_particle="pid > -1",
        infile=ladim_file,
        outfile=outfile,
    )
    ladim_aggregate.run_conf(conf)


def create_weights(feed_df, ladim_dset):
    import numpy as np
    import xarray as xr
    import netCDF4 as nc

    # Convert from long form to table form
    feed_df['release_time'] = feed_df['time'].values.astype('datetime64[s]').astype('int64')
    feed_df = feed_df[['release_time', 'poly_id', 'feed']].set_index(['release_time', 'poly_id'])
    feed_dset = feed_df.to_xarray()
    feed_dset['feed'] = feed_dset['feed'].fillna(0)

    # Count number of particles released for each category
    import ladim_aggregate
    with nc.Dataset('count.nc', 'w', diskless=True) as count_dset:
        time_bins = feed_dset['release_time'].values.tolist()
        last_entry = np.diff(time_bins[-2:]) + time_bins[-1]
        time_bins += last_entry.tolist()
        conf = dict(
            bins=dict(release_time=time_bins, poly_id='group_by'),
            filter_particle="pid > -1",
            infile=ladim_dset,
            outfile=count_dset,
        )
        ladim_aggregate.run_conf(conf)
        feed_dset['pcount'] = xr.DataArray(
            data=count_dset.variables['histogram'][:],
            coords=dict(poly_id=count_dset.variables['poly_id'][:]),
            dims=('release_time', 'poly_id'),
        ).sel(poly_id=feed_dset['poly_id'])

    feed_dset['feed_per_particle'] = feed_dset['feed'] / np.maximum(feed_dset['pcount'], 1)
    return feed_dset

def convert_feed_table_to_matrix_form(feed_df):
    feed_df['release_time'] = feed_df['time'].values.astype('datetime64[s]').astype('int64')
    feed_df = feed_df[['release_time', 'poly_id', 'feed']].set_index(['release_time', 'poly_id'])
    feed_dset = feed_df.to_xarray()
    feed_dset['feed'] = feed_dset['feed'].fillna(0)
    return feed_dset


def create_crecon_file_for_particle_counting(stream, outfile, ladim_file):
    import importlib.resources
    from . import templates
    resource_file = importlib.resources.files(templates).joinpath('crecon1.yaml')
    txt_template = resource_file.read_text(encoding='utf-8')
    txt = txt_template.format(
        crecon_output_file=outfile,
        ladim_output_file=ladim_file,
    )
    stream.write(txt)


def create_crecon_file_for_concentration(
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


def compute_feed_rate(feed_df):
    import numpy as np
    import xarray as xr

    # Convert from long form to table form
    feed_df['release_time'] = feed_df['time'].values.astype('datetime64[s]').astype('int64')
    feed_df = feed_df[['release_time', 'poly_id', 'feed']].set_index(['release_time', 'poly_id'])
    feed_dset = feed_df.to_xarray()
    feed_dset['feed'] = feed_dset['feed'].fillna(0)

    # Compute feed rate (kg per day)
    sec_diff = np.diff(feed_dset['release_time'].values.astype('datetime64[s]').astype('int64'))
    sec_diff = xr.Variable('release_time', np.concatenate([sec_diff, [sec_diff[-1]]]))
    days_diff = sec_diff / (60 * 60 * 24)
    feed_dset['rate'] = feed_dset['feed'] / days_diff
    feed_dset['rate'].attrs['units'] = 'kg/day'
    feed_dset['rate'].attrs['long_name'] = 'mean feeding rate'

    return feed_dset['rate']
