def make_concentration(config):
    crecon_count_fname = config['root_dir'] / config['concentration']['count_conf_file']
    with open(crecon_count_fname, 'w', encoding='utf-8') as fp:
        create_crecon_file_for_particle_counting(fp)

    count_fname = config['root_dir'] / config['concentration']['count_file']
    create_particle_count_file(crecon_count_fname, count_fname)

    crecon_conc_file = config['root_dir'] / config['concentration']['conc_conf_file']
    with open(crecon_conc_file, 'w', encoding='utf-8') as fp:
        create_crecon_file_for_concentration(fp)

    conc_fname = config['root_dir'] / config['concentration']['conc_file']
    create_concentration_file(crecon_conc_file, conc_fname)


def create_crecon_file_for_particle_counting(stream):
    import importlib.resources
    from . import templates
    resource_file = importlib.resources.files(templates).joinpath('crecon1.yaml')
    txt = resource_file.read_text(encoding='utf-8')
    stream.write(txt)


def create_crecon_file_for_concentration(stream):
    import importlib.resources
    from . import templates
    resource_file = importlib.resources.files(templates).joinpath('crecon1.yaml')
    txt = resource_file.read_text(encoding='utf-8')
    stream.write(txt)


def create_particle_count_file(input_file, output_file):
    import xarray as xr
    conc_dset = xr.Dataset()
    conc_dset.to_netcdf(output_file)


def create_concentration_file(input_file, output_file):
    import xarray as xr
    conc_dset = xr.Dataset()
    conc_dset.to_netcdf(output_file)
