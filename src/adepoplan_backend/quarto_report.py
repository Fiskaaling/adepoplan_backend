def make_quarto_report(config):
    """
    Make report using supplied config parameters

    :param config: Config parameter dict
    """
    # Create ladim output file
    quarto_config_txt = get_quarto_text()
    quarto_config_file_name = config['root_dir'] / 'quarto_report.qmd'
    with open(quarto_config_file_name, 'w', encoding='utf-8') as fp:
        fp.write(quarto_config_txt)

    # get user input parameters
    fname = quarto_config_file_name
    count_file=config['concentration']['count_file']
    conc_file=config['concentration']['conc_file']
    test = 10

    # render quarto
    import quarto

    quarto.render(input=fname, 
                  execute_params={'test':test,
                                  'count_file':count_file,
                                  'conc_file':conc_file})
    

def copy_quarto_template_to_folder(config):
    # copy template quarto to the current folder
    import importlib.resources
    from . import templates
    import shutil

    template_resources = importlib.resources.files(templates)
    template_file = template_resources.joinpath('quarto_report.qmd')

    destination_file = config['root_dir'] / 'quarto_report.qmd'

    shutil.copyfile(template_file, destination_file)

def get_quarto_text():
    import importlib.resources
    from . import templates
    template_resources = importlib.resources.files(templates)
    txt = template_resources.joinpath('quarto_report.qmd').read_text(encoding='utf-8')
    return txt