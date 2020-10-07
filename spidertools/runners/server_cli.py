from flask import Flask, g, request
from flask_cors import CORS
import sqlite3
import yaml
import json
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler
from spidertools.data.processor import ProcessDataBuilder
from spidertools.data.selectors import filter_selector, sort_selector
from spidertools.utils.timer import timer
from typing import List

def create_app(data_base_path):
    app = Flask(__name__)
    CORS(app)


    DATABASE_PATH = data_base_path

    
    @app.route('/', methods=['GET'])
    @timer
    def hello_world():
        return "Hello World!", 200   

    
    @app.route('/projects/', methods=['GET'])
    @timer
    def list_projects():
        project_handler = ProjectTableHandler(DATABASE_PATH)
        if (results := project_handler.get_projects()) is None:
            return {"Error": "No projects found..."}, 404

        return {"projects": project_handler.get_projects()}, 200

    
    @app.route('/commits/<project_name>', methods=['GET'])
    @timer
    def list_commits_of_project(project_name):
        project_handler = ProjectTableHandler(DATABASE_PATH)
        
        if (project_id := project_handler.get_project_id(project_name)) is None:
            return {"Error": f"Project '{project_name}' was not found..."}, 404

        commit_handler = CommitTableHandler(DATABASE_PATH)
        if (commits := commit_handler.get_all_commits(project_id)) is None:
            return {"Error": f"No commits for '{project_name}' were not found..."}, 404

        return {
            "project": project_name,
            "commits": commits
        }, 200

    
    @app.route('/coverage/<project_name>/<commit_sha>', methods=['GET'])
    @timer
    def coverage(project_name, commit_sha):
        project_handler = ProjectTableHandler(DATABASE_PATH)
        commit_handler = CommitTableHandler(DATABASE_PATH)
        coverage_handler = MethodCoverageHandler(DATABASE_PATH)

        # Get all the necessary data
        if (project_id := project_handler.get_project_id(project_name)) is None:
            return {"Error": f"Project '{project_name}' not found..."}, 404

        if (commit_id := commit_handler.get_commit_id(project_id, commit_sha)) is None:
            return {"Error": f"No commit '{commit_sha}' found in project: '{project_name}'..."}, 404

        coverage = coverage_handler.get_project_coverage(commit_id)

        # Filter and sort data using the given parametrs.
        sort_function = list()
        filter_functions = list()

        # filter_functions.append(filter_selector("num_tests"))
        # filter_functions.append(filter_selector("test_coverage"))
        # filter_functions.append(filter_selector("test_result"))

        if (f := sort_selector("name")) is not None:
            sort_function.append(f)

        # filter and sort the data
        coverage = ProcessDataBuilder() \
            .add_sorters(sort_function) \
            .process_data(coverage)

        return {
            "project": project_name,
            "commit_sha": commit_sha,
            "coverage": coverage
        }, 200

    return app

def load_configuration(configuration_file_path):
    with open (configuration_file_path) as config_file:
        config = yaml.safe_load(config_file)
    
    HOST = config['server']['host']
    PORT = config['server']['port']
    DATABASE_PATH = config['server']['database_path']

    print(f"Load database: {DATABASE_PATH}")
    return HOST, PORT, DATABASE_PATH

def main():
    # Load configurations
    configuration_file = '.spider.yml'
    HOST, PORT, DATABASE_PATH = load_configuration(configuration_file)

    # Initialize the flask application
    app = create_app(DATABASE_PATH)

    # Start the debug server
    app.run(debug=True, host=HOST, port=PORT)
