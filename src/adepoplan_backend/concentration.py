def make_concentration(config):
    import ladim_aggregate

    ladim_output_file = config['root_dir'] / config['particles']['file']

    crecon_count_fname = config['root_dir'] / config['concentration']['count_conf_file']
    count_fname = config['root_dir'] / config['concentration']['count_file']
    with open(crecon_count_fname, 'w', encoding='utf-8') as fp:
        create_crecon_file_for_particle_counting(fp, count_fname, ladim_output_file)

    ladim_aggregate.main(str(crecon_count_fname))

    crecon_conc_fname = config['root_dir'] / config['concentration']['conc_conf_file']
    conc_fname = config['root_dir'] / config['concentration']['conc_file']
    with open(crecon_conc_fname, 'w', encoding='utf-8') as fp:
        create_crecon_file_for_concentration(fp, conc_fname, ladim_output_file)

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


def create_crecon_file_for_concentration(stream, outfile, ladim_file):
    import importlib.resources
    from . import templates
    resource_file = importlib.resources.files(templates).joinpath('crecon1.yaml')
    txt_template = resource_file.read_text(encoding='utf-8')
    txt = txt_template.format(
        crecon_output_file=outfile,
        ladim_output_file=ladim_file,
    )
    stream.write(txt)
