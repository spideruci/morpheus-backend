# Morpheus tools

## Install
```
python3 -m virtualenv venv/
pip install -e .
```

## Usage
After installing the tool can be run using just the `matrix` command.

```
$ matrix --help
usage: Matrix [-h] {analyze,db,server,extract} ...

Collection of tools used to analyze, store, and serve the historical coverage data for the morpheus visualization.

positional arguments:
  {analyze,db,server,extract}
    analyze             Obtain historical coverage data from repository.
    db                  Create database with morpheus coverage data.
    server              Start server
    extract             Extract Morpheus coverage data from databse

options:
  -h, --help            show this help message and exit
```

NOTES:
- Tacoco and parser location are configured in the `.env` file. 

### analyze

Example command to get the coverage of all tagged commits for jpacman-framework: `matrix analyze https://github.com/SERG-Delft/jpacman-framework.git  ./historical-coverage-json --tags -1`

### db

After coverage data has been obtained we can create a database out of all the data to make querying easier: `matrix db ./historical-data-json/ ./jpacman-history.sqlite`

### extract

Turning the database into static json files

`matrix extract ./jpacman-history.sqlite ./history-static/`

### server

`matrix server ./jpacman-history.sqlite --port 8080 --host 127.0.0.1`
