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
