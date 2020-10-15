from flask import Flask, g, request
from flask_cors import CORS
import yaml
from spidertools.storage.db_helper import DatabaseHelper, row2dict
from spidertools.storage.query.querybuilder import MethodCoverageQuery, ProjectQuery, CommitQuery
from spidertools.storage.query.output_formatter import coverage_format
from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.data.selectors import sort_selector
from spidertools.storage.data.processor import ProcessDataBuilder
from spidertools.utils.timer import timer
from typing import List
import logging

logger = logging.getLogger(__name__)

def create_app(data_base_path, echo=False):
    app = Flask(__name__)
    CORS(app)

    db_helper: DatabaseHelper = DatabaseHelper(data_base_path, echo)
    
    @app.route('/', methods=['GET'])
    @timer
    def hello_world():
        return "Hello World!", 200   

    @app.route('/projects', methods=['GET'])
    @timer
    def list_projects():
        with db_helper.create_session() as session:
            projects = ProjectQuery(session).get_projects()
        
        if len(projects) == 0:
            return {"Error": "No projects found..."}, 404
        
        return {"projects": list(map(row2dict, projects))}, 200

    
    @app.route('/commits/<project_name>', methods=['GET'])
    @timer
    def list_commits_of_project(project_name):
        
        with db_helper.create_session() as session:
            project: Project = ProjectQuery(session).get_project(project_name)

            if project is None:
                return {"Error": "Project not found..."}, 404

            commits = CommitQuery(session).get_commits(project)

        if len(commits) == 0:
            return {"Error": f"Project '{project_name}' was not found..."}, 404

        return {
            "project": project_name,
            "commits": list(map(row2dict, commits))
        }, 200

    
    @app.route('/coverage/<project_name>/<commit_sha>', methods=['GET'])
    @timer
    def coverage(project_name, commit_sha):
        # TODO add error handling (commit not found, project not found)
        filters = []

        # TODO Add test/method filter parameter
        with db_helper.create_session() as session:
            
            project: Project = ProjectQuery(session).get_project(project_name=project_name)
            if project is None:
                return {"Error": "Project not found..."}, 404

            commit: Commit = CommitQuery(session).get_commit(project, commit_sha)
            logger.debug(f"\n\n{project}/{commit}\n\n")

            if commit is None:
                return {"Error": "Commit not found..."}, 404

            coverage_query = MethodCoverageQuery(session)\
                .set_commit(commit)\
                .set_project(project)

            for filter in filters:
                coverage_query.add_filter(filter)

            edges = coverage_query.get_coverage()
            methods = coverage_query.get_methods()
            tests = coverage_query.get_tests()

        # Format coverage data
        coverage = coverage_format(methods, tests, edges)

        # Filter and sort data using the given parametrs.
        # sort_function = list()
        # filter_functions = list()

        # if (f := sort_selector("name")) is not None:
        #     sort_function.append(f)

        # # filter and sort the data
        # coverage = ProcessDataBuilder() \
        #     .add_sorters(sort_function) \
        #     .process_data(coverage)

        return {
            "project": project_name,
            "commit_sha": commit_sha,
            "coverage": coverage
        }, 200

    return app

    @app.route('/history/<project_name>/<method_name>', methods=['GET'])
    @timer
    def history(project_name, method_name):
        with db_helper.create_session() as session:
            # Get project
            project: Project = ProjectQuery(session).get_project(project_name)
            
            # Get versions of method
            # method: ProdMethod = MethodCoverageQuery(session).get_method(method_name)
            
            # Obtain all tests that cover each version of the method and see if passed or failed
            # MethodCoverageQuery(session).get_tests(method)

        return 501

def load_configuration(configuration_file_path):
    with open (configuration_file_path) as config_file:
        config = yaml.safe_load(config_file)
    
    HOST = config['server']['host']
    PORT = config['server']['port']
    DATABASE_PATH = config['server']['database_path']

    logging.info("Load database: %s", DATABASE_PATH)
    return HOST, PORT, DATABASE_PATH

def init_logger(logging_level=logging.INFO):
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def main():
    # Load configurations
    configuration_file = '.spider.yml'
    HOST, PORT, DATABASE_PATH = load_configuration(configuration_file)

    # Initialize the flask application, with debugging parameters
    init_logger()
    app = create_app(DATABASE_PATH, echo=True)

    # Enable timers to get performance data on t
    timer.enabled = True
    # Start the debug server
    app.run(debug=True, host=HOST, port=PORT)
