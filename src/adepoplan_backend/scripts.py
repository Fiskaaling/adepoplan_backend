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

    # --- Build step: Create quarto report ---
    import adepoplan_backend.quarto_report
    adepoplan_backend.quarto_report.make_quarto_report(config)


def read_config(fname):
    import json
    from pathlib import Path

    with open(fname, encoding='utf-8') as fp:
        config = json.load(fp)

    config['root_dir'] = Path(fname).parent.absolute()
    return config
