def make_concentration(config):
    import ladim_aggregate
    import pandas as pd
    import yaml
    import numpy as np

    # Compute filter max age
    ladim_input_file = config['root_dir'] / 'ladim.yaml'
    max_age = np.timedelta64(config['user_input']['max_age'], 's')
    with open(ladim_input_file, encoding='utf-8') as fp:
        output_freq = yaml.safe_load(fp)['output_variables']['outper']
        filter_max_age = max_age - np.timedelta64(output_freq[0], output_freq[1])

    # Step 1: Create particle count config file
    ladim_output_file = config['root_dir'] / config['particles']['file']
    crecon_count_fname = config['root_dir'] / config['concentration']['count_conf_file']
    count_fname = config['root_dir'] / config['concentration']['count_file']
    with open(crecon_count_fname, 'w', encoding='utf-8') as fp:
        create_crecon_file_for_particle_counting(fp, count_fname, ladim_output_file)

    # Step 2: Create concentration config file
    crecon_conc_fname = config['root_dir'] / config['concentration']['conc_conf_file']
    conc_fname = config['root_dir'] / config['concentration']['conc_file']
    feed_factor = config['user_input']['feed_factor']
    weight_file = config['root_dir'] / config['concentration']['weight_file']
    with open(crecon_conc_fname, 'w', encoding='utf-8') as fp:
        create_crecon_file_for_concentration(
            stream=fp, outfile=conc_fname, ladim_file=ladim_output_file,
            feed_factor=feed_factor, weight_file=weight_file,
            count_file=count_fname, cell_area=100,
            max_age=filter_max_age.astype('timedelta64[s]').astype('int64'),
        )

    # Step 3: Compute the feeding rate (kg per day)
    feed_file = config['root_dir'] / config['concentration']['feed_file']
    feed_df = pd.read_csv(feed_file)
    feed_rate = compute_feed_rate(feed_df)
    feed_rate.to_netcdf(weight_file)

    # Step 4: Count the particles
    ladim_aggregate.main(str(crecon_count_fname))

    # Step 5: Compute concentrations
    ladim_aggregate.main(str(crecon_conc_fname))


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
        stream, outfile, ladim_file, feed_factor, weight_file, count_file,
        cell_area, max_age,
):
    import importlib.resources
    from . import templates
    resource_file = importlib.resources.files(templates).joinpath('crecon2.yaml')
    txt_template = resource_file.read_text(encoding='utf-8')
    txt = txt_template.format(
        crecon_output_file=outfile,
        ladim_output_file=ladim_file,
        feed_factor=feed_factor,
        weight_file=weight_file,
        count_file=count_file,
        cell_area=cell_area,
        max_age=max_age,
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
