def make_quarto_report(config):
    """
    Make report using supplied config parameters

    :param config: Config parameter dict
    """
    
    # copy the template
    copy_quarto_template_to_folder(config)

    # get user input parameters
    count_file=config['concentration']['count_file']
    conc_file=config['concentration']['conc_file']

    # quarto render in terminal
    import os

    os.system("quarto render quarto_report.qmd --to html -P count_file:count_file -P conc_file:conc_file -P test:10")

    # other option is to put all parameters in a yaml file
    #os.system("quarto render quarto_report.qmd --to html --execute-params params.yaml")


def copy_quarto_template_to_folder(config):
    # copy template quarto to the current folder
    import importlib.resources
    from . import templates
    import shutil

    template_resources = importlib.resources.files(templates)
    template_file = template_resources.joinpath('quarto_report.qmd')

    destination_file = config['root_dir'] / 'quarto_report.qmd'

    shutil.copyfile(template_file, destination_file)