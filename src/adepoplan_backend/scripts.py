def main(*args):
    config_file_name = args[0]
    config = read_config(config_file_name)

    # --- Build step: Create release file ---
    import adepoplan_backend.release
    adepoplan_backend.release.make_release(config)

    # --- Build step: Create ladim output file ---
    import adepoplan_backend.particles
    adepoplan_backend.particles.make_particles(config)

    # --- Build step: Create concentration file ---
    import adepoplan_backend.concentration
    adepoplan_backend.concentration.make_concentration(config)

    # --- Build step: Create final report ---
    import adepoplan_backend.report
    adepoplan_backend.report.make_report(config)


def read_config(fname):
    import json
    from pathlib import Path
    import importlib.resources
    from . import templates

    templ_res = importlib.resources.files(templates)
    with templ_res.joinpath('adepoplan.json').open(encoding='utf-8') as fp:
        default_config = json.load(fp)

    with open(fname, encoding='utf-8') as fp:
        user_config = json.load(fp)

    config = merge_dict(default_config, user_config)
    config['root_dir'] = Path(fname).parent.absolute()
    return config


def merge_dict(first, second):
    result = {k: v for k, v in first.items() if k not in second}

    for k, v in second.items():
        if (k in first) and isinstance(v, dict) and isinstance(first[k], dict):
            result[k] = merge_dict(first[k], v)
        else:
            result[k] = v

    return result
