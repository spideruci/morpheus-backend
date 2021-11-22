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
- Location of analysis tools, [Tacoco](https://github.com/spideruci/tacoco/) and [java method parser](https://github.com/kajdreef/java-method-parser), are configured in the `.env` file.

### analyze

Example command to get the coverage of all tagged commits for jpacman-framework: `matrix analyze https://github.com/SERG-Delft/jpacman-framework.git  ./historical-coverage-json --tags -1`

### db

After coverage data has been obtained we can create a database out of all the data to make querying easier:
- `matrix db --all ./historical-data-json/ ./history.sqlite`
- `matrix db --project ./historical-data-json/jpacman-framework/ ./history-jpacman-framework.sqlite`

### extract

Turning the database into static json files

`matrix extract ./history-jpacman-framework.sqlite ./history-static/`

### server

`matrix server ./history-jpacman-framework.sqlite --port 8080 --host 127.0.0.1`



## ToDo:
- Automaticaly remove unnecessary files:
  - coverage.{json,exec,err,log}
- What steps do we need to compile/test-compile project
  - most projects: compile -> test-compile
  - Guava: install needs to be performed?
    - Add flag to do install first?
- Catch when unique methods/tests occur, rollback what has been inserted and stop program
  - Why? Allowing us to fix mistakes and try to run the tool again it becomes easier to reproduce.
  - Database is still useless though.