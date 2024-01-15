def make_concentration(config):
    import xarray as xr
    conc_fname = config['root_dir'] / config['concentration']['count_file']
    conc_dset = xr.Dataset()
    conc_dset.to_netcdf(conc_fname)

    conc_fname = config['root_dir'] / config['concentration']['conc_file']
    conc_dset = xr.Dataset()
    conc_dset.to_netcdf(conc_fname)
