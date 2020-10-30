# SpiderTools

Create a python wrapper around the following SpiderLab tools:

- [x] [Tacoco](https://github.com/spideruci/tacoco)
- [ ] [Blinky-Core](https://github.com/spideruci/blinky-core)

The goal is to allow us to write experiments in Python without having to relearn how each tool exactly works.

## Install
- The SpiderTools can be installed using the following commands:
```
git clone https://github.com/kajdreef/spidertools
cd spidertools
virtualenv venv -p <path-to-python3.8>
. ./venv/bin/activate
python -m pip install -e .
```

## Commands:

- `spider-serve`: Starts backend server with the following endpoints (can be found in [server_cli.py](./spidertools/runners/server_cli.py))
    - `/projects`: returns a list of projects
    - `/commits/<project_name>`: returns a list of commits from specified project (obtained through projects endpoint)
    - `/coverage/<project_name>/<commit_sha>`: returns a list of methods, tests, and edges from specified project and commit
    - `/history/<project_name>/<method_id>`: Work in progress
- `pluperfect`: Our data collecting tool
    - `pluperfect --help`: provides inormation on how to run the tool
    - Example `pluperfect https://github.com/serg-delft/jpacman-template --config .spider.yml --current`
        - Runs the analysis on the project: `https://github.com/serg-delft/jpacman-template`
        - Using the configuation file `.spider.yml`
        - `--current` specifies that it is only run on the latest commit
            - can be changed to --tags/--commits with a number to run on the last X tags or last X commits.

## Development
- Dependencies:
    - Python3.8
    - tox
    - [optional/recommended] virtualenv

- Running Tests: `tox`

To make use of the wrappers the tools itself need to be installed as well, see the documentation for each project how to do that.
