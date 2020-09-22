from flask import Flask, g, request
from flask_cors import CORS
import sqlite3
import yaml
import json
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler
from spidertools.data.sorting import name
from spidertools.data.processor import ProcessDataBuilder
from typing import List

app = Flask(__name__)
CORS(app)

DATABASE_PATH = ""
HOST = "localhost"
PORT = 5000

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello World!", 200   

@app.route('/projects/', methods=['GET'])
def list_projects():
    project_handler = ProjectTableHandler(DATABASE_PATH)
    if (results := project_handler.get_projects()) is None:
        return {"Error": "No projects found..."}, 404

    return {"projects": project_handler.get_projects()}, 200

@app.route('/commits/<project_name>', methods=['GET'])
def list_commits_of_project(project_name):
    project_handler = ProjectTableHandler(DATABASE_PATH)
    
    if (project_id := project_handler.get_project_id(project_name)) is None:
        return {"Error": f"Project '{project_name}' was not found..."}, 404

    commit_handler = CommitTableHandler(DATABASE_PATH)
    if (commits := commit_handler.get_all_commits(project_id["project_id"])) is None:
        return {"Error": f"No commits for '{project_name}' were not found..."}, 404

    return {
        "project": project_name,
        "commits": commits
    }, 200

@app.route('/coverage/<project_name>/<commit_sha>', methods=['GET'])
def coverage(project_name, commit_sha):
    project_handler = ProjectTableHandler(DATABASE_PATH)
    commit_handler = CommitTableHandler(DATABASE_PATH)
    coverage_handler = MethodCoverageHandler(DATABASE_PATH)

    # Get all the necessary data
    if (project_id := project_handler.get_project_id(project_name)) is None:
        return {"Error": f"Project '{project_name}' not found..."}, 404

    if (commit_id := commit_handler.get_commit_id(project_id['project_id'], commit_sha)) is None:
        return {"Error": f"No commit '{commit_sha}' found in project: '{project_name}'..."}, 404

    coverage = coverage_handler.get_project_coverage(commit_id['commit_id'])

    # Set up filter and sort functionality.
    sort_methods = {
        "name": sort_by_name,

        # sort production axis
        "prod_name": lambda x: x,

        # sort test axis
        "test_name": lambda x: x
    }

    filter_methods = {
        # General filters

        # Test filters
        "result": lambda x: x, # Filter based on if a test passed or failed
        "num_tests": lambda x: x, # Filter based on number of tests < or > or == (Can be used to filter out methods that have no tests.) (no range)
        "coverage": lambda x: x, # Filter test methods based on the number of methods they cover.

        # Production filters
        "cluster": lambda x: x, # Filter out all production methods not belonging to a specific cluster
        "package": lambda x: x, # Filter out all production methods not part of the specified package
        "class": lambda x: x, # Filter out all production methods not part of the specified class
        "method": lambda x: x, # Filter to a specific production method
    }

    sort_function = None
    filter_functions = list()

    # Get parameters
    # TODO this is not going to work for multiple filters and a single sort where we may have multiple parameters.
    #  - Fix could be to add json to the url as the parameter value of filter and sort.
    filter_arguments = request.args.get("filters", default="{}", type=str)
    filter_types: List = json.loads(filter_arguments)
    sort_type = request.args.get("sorting", default="name")

    # Get the corresponding filter/sort functions
    if sort_type in sort_methods:
        sort_function = sort_methods.get(sort_type)

    # TODO encode the parameters in here as well...
    for filter_type, parameters in filter_types.items():
        if filter_type in filter_methods:
            filter_functions.append(filter_methods.get(filter_type))   

    # filter and sort the data
    coverage = ProcessDataBuilder() \
        .add_filters(filter_functions) \
        .set_sorter(sort_function) \
        .process_data(coverage)

    return {
        "project": project_name,
        "commit_sha": commit_sha,
        "coverage": coverage
    }, 200

def load_configuration(configuration_file_path):
    global HOST, PORT, DATABASE_PATH
    with open (configuration_file_path) as config_file:
        config = yaml.safe_load(config_file)
    
    HOST = config['server']['host']
    PORT = config['server']['port']
    DATABASE_PATH = config['server']['database_path']
    print(f"Load database: {DATABASE_PATH}")


def main():
    global HOST, PORT

    # Load configurations
    configuration_file = '.spider.yml'
    load_configuration(configuration_file)

    # Start the debug server
    app.run(debug=True, host=HOST, port=PORT)