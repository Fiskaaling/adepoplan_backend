def make_report(config):
    """
    Make report using supplied config parameters

    :param config: Config parameter dict
    """
    txt = load_report_template()
    outfile = config['root_dir'] / config['report']['file']
    with open(outfile, 'w', encoding='utf-8') as fp:
        fp.write(txt)


def load_report_template():
    import importlib.resources
    pkg_name = str(__name__).split(sep='.', maxsplit=1)[0]
    templates = importlib.resources.files(pkg_name).joinpath('templates')
    return templates.joinpath('report.html').read_text('utf-8')
