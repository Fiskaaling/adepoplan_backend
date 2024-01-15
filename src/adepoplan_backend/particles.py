
def make_particles(config):
    # Create ladim output file
    ladim_config_txt = get_ladim_config_text(
        start_time=config['user_input']['start_time'],
        stop_time=config['user_input']['stop_time'],
        output_file=config['particles']['file'],
    )
    ladim_config_file_name = config['root_dir'] / 'ladim.yaml'
    with open(ladim_config_file_name, 'w', encoding='utf-8') as fp:
        fp.write(ladim_config_txt)

    # Run ladim simulation (change working directory first)
    import ladim
    import io
    import os
    config_stream = io.StringIO(ladim_config_txt)
    prevdir = os.getcwd()
    try:
        os.chdir(config['root_dir'])
        ladim.main(config_stream)
    finally:
        # Return to previous working directory
        os.chdir(prevdir)


def get_ladim_config_text(**kwargs):
    import importlib.resources
    from . import templates
    template_resources = importlib.resources.files(templates)
    txt = template_resources.joinpath('ladim.yaml').read_text(encoding='utf-8')
    return txt.format(**kwargs)
