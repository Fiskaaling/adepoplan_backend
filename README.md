# adepoplan_backend

This program creates a deposition simulation from a json configuration
file. The output consists of many files, including figures, tables and a
formatted report which presents the results of the simulation.

## Installation

First, install `conda` and create an environment using the in-repo definition
file `conda.yaml`:

    conda env create -f conda.yaml

Then, install the package using `pip`:
    
    pip install git+https://github.com/Fiskaaling/adepoplan_backend.git


## Usage

The program initiates a build chain, where each build step creates new files
that are created on top of existing files in the build directory. Initially,
the build directory should contain three files:

- `adepoplan.json`: Configuration parameters specified by user interface
- `cages.geojson`: A geojson file with one polygon for each fish farm cage
- `feed.csv`: A table of feeding data

The program is executed from python as

    python -m adepoplan_backend adepoplan.json

where the location of `adepoplan.json` (which may be specified as a full path)
also defines the build directory.  

The program will generate a particle tracking simulation, aggregate the results
into a concentration map, generate some figures and a simple report.

The structure of the input files are documented as comments in the example
files, which are located in `tests/end_to_end/ex1`.


## Future work TODO/wish list

Issues:
- indexing error in concentration, where geojson cannot have poly_id that is not referenced in the production_data file
- something strange happens when particles_per_day = 100
    - this might be a me (aka Birgitta) problem 

TODO:
- using pultiple forcing files to cover larger area
- set up preselected boundary boxes for the different fjords/sounds

Nice to have: 
- write relevant information into the attributes of the .nc files, such as:
    - forcing used
    - particle liifespan
    - taucrit
    - vertical mixing
    - numerics setup
- easy way to separate the steps
    - e.g. 
        - one: release particles from all cages
        - one: ladim for all cages
        - multiple: crecon
            - test out different production data and thus weights
    - e.g.
        - one release
        - multiple ladim, testing different taucrit
        - one crecon pr. ladim output