from flask import Flask, g
import sqlite3
import yaml
import json
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler

app = Flask(__name__)

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

    if (project_id := project_handler.get_project_id(project_name)) is None:
        return {"Error": f"Project '{project_name}' not found..."}, 404

    if (commit_id := commit_handler.get_commit_id(project_id['project_id'], commit_sha)) is None:
        return {"Error": f"No commit '{commit_sha}' found in project: '{project_name}'..."}, 404

    return {
        "project": project_name,
        "commit_sha": commit_sha,
        "coverage": coverage_handler.get_project_coverage(commit_id['commit_id'])
    }, 200


def load_configuration(configuration_file_path):
    global HOST, PORT, DATABASE_PATH
    with open (configuration_file_path) as config_file:
        config = yaml.safe_load(config_file)
    
    HOST = config['server']['host']
    PORT = config['server']['port']
    DATABASE_PATH = config['server']['database_path']


def main():
    global HOST, PORT

    # Load configurations
    configuration_file = '.spider.yml'
    load_configuration(configuration_file)

    # Start the debug server
    app.run(debug=True, host=HOST, port=PORT)