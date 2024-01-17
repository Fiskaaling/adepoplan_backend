import numpy as np


def make_release(config):
    # Create makrel output file
    makrel_config_txt = get_makrel_config_text(
        start_time=config['user_input']['start_time'],
        stop_time=config['user_input']['stop_time'],
        makrel_area_file=config['root_dir'] / config['release']['area_file'],
        min_release_depth=config['user_input']['min_release_depth'],
        max_release_depth=config['user_input']['max_release_depth'],
        sinkvel_knots=config['user_input']['sinkvel_knots'],
        sinkvel_cdf=config['user_input']['sinkvel_cdf'],
        num_particles=compute_number_of_particles(
            start=config['user_input']['start_time'],
            stop=config['user_input']['stop_time'],
            num_per_day=config['release']['particles_per_day'],
        )
    )
    makrel_config_file_name = config['root_dir'] / 'makrel.yaml'
    with open(makrel_config_file_name, 'w', encoding='utf-8') as fp:
        fp.write(makrel_config_txt)

    # Create release file
    from ladim_plugins.release import make_release
    out_file = config['root_dir'] / config['release']['release_file']
    make_release(str(makrel_config_file_name), out_file)


def get_makrel_config_text(**kwargs):
    import importlib.resources
    from . import templates
    template_resources = importlib.resources.files(templates)
    txt = template_resources.joinpath('makrel.yaml').read_text(encoding='utf-8')
    return txt.format(**kwargs)


def compute_number_of_particles(start, stop, num_per_day):
    start_time = np.datetime64(start)
    stop_time = np.datetime64(stop)
    num_days = (stop_time - start_time) / np.timedelta64(1, 'D')
    num_particles = int(np.round(num_per_day * num_days))
    return num_particles
