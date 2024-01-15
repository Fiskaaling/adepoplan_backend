def main(*args):
    config_file_name = args[0]
    config = read_config(config_file_name)

    import adepoplan_backend.report
    adepoplan_backend.report.make_report(config)


def read_config(fname):
    import json
    from pathlib import Path

    with open(fname, encoding='utf-8') as fp:
        config = json.load(fp)

    config['root_dir'] = Path(fname).parent.absolute()
    return config
