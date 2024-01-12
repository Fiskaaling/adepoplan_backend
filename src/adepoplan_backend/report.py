def load_report_template():
    import importlib.resources
    pkg_name = str(__name__).split(sep='.', maxsplit=1)[0]
    templates = importlib.resources.files(pkg_name).joinpath('templates')
    return templates.joinpath('report.html').read_text('utf-8')
