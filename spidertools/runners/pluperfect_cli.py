import argparse
import os
import yaml
import json
import logging
from typing import Tuple
from spidertools.utils.analysis_repo import AnalysisRepo
from spidertools.tools.tacoco import TacocoRunner
from spidertools.tools.history import MethodParserRunner
from spidertools.storage.db_helper import DatabaseHelper
from spidertools.storage.parsing.methods import MethodParser
from spidertools.storage.parsing.tacoco import TacocoParser
from spidertools.storage.models.repository import Commit, Project
 
logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse arguments to run pluperfect
    """
    parser = argparse.ArgumentParser(description='Run Tacoco')

    parser.add_argument('project_url', type=str, help="Absolute path or url to system-under-test.")
    parser.add_argument('--output_path', type=str, help="absolute path to output directory")
    parser.add_argument('--config', type=str, help="absolute path to tacoco")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--current', action='store_true', help="Run the analysis on current version of the code")
    group.add_argument('--tags', type=int, help="Run the analysis on specified amount of tags, -1 would be all tags")
    group.add_argument('--commits', type=int, help="Run the analysis on specified amount of commits, -1 would be all commits")

    return parser.parse_args()

def start(DB_PATH, project_url, output_path, tacoco_path, history_slider_path, arguments):
    db_handler = DatabaseHelper(DB_PATH)

    with AnalysisRepo(project_url) as repo:
        # TODO Add in error handling for existing commits/projects
        logger.info("Project: %s", repo.get_project_name())

        # Add project
        project = Project(project_name=repo.get_project_name())

        # Analysis tools
        tacoco_runner = TacocoRunner(repo, output_path, tacoco_path)
        parser_runner = MethodParserRunner(repo, output_path, history_slider_path)

        # Get all commits we want to run the analysis on.
        commits = []
        if arguments.current:
            commits = [repo.get_current_commit()]
        elif arguments.tags is not None:
            commits = repo.iterate_tagged_commits(arguments.tags)
        elif arguments.commits is not None:
            commits = repo.iterate_commits(arguments.commits)
        else:
            print("The run was misconfigured...")
            exit(0)
        
        for commit in commits:
            logger.info("[INFO] Analyze commit: %s", commit)
            # Add commit to the database
            commit = Commit(sha=commit)

            # Run analysis and return paths to output files
            success, method_file_path, tacoco_file_path = _analysis(repo, tacoco_runner, parser_runner, output_path)
            
            if not success:
                logger.error('Analysis for %s failed...', commit)
                continue

            with open(method_file_path) as method_file:
                method_parser = MethodParser()\
                    .set_commit(commit)

                coverage = method_parser\
                    .parse(json.load(method_file))
                method_parser.store(
                    db_helper=db_handler,
                    project=project,
                    commit=commit,
                    methods=coverage
                )

            with open(tacoco_file_path) as tacoco_file:
                tacoco_parser = TacocoParser()
                coverage = tacoco_parser\
                    .parse(json.load(tacoco_file))

                tacoco_parser.store(
                    db_helper=db_handler,
                    project=project,
                    commit=commit,
                    coverage=coverage
                )

def _analysis(repo, tacoco_runner, parser_runner, output_path) -> Tuple[bool, str, str]:
    # Before each analysis remove all generated files of previous run
    repo.clean()

    # Try compiling the project
    try:
        tacoco_runner \
            .compile() \
            .test_compile()
    except Exception as e:
        logger.error("build failure...")
        return (False, None, None)

    # Start analysis
    parser_runner.run()
    tacoco_runner.run()

    # Combine data
    commit_sha = repo.get_current_commit()
    project_output_path = f"{output_path}{os.path.sep}{repo.get_project_name()}{os.path.sep}"

    logger.info("build successfull...")
    return (True,
        f"{project_output_path}methods-{commit_sha}.json",
        f"{project_output_path}{commit_sha}-cov-matrix.json"
    )

def init_logger(logging_level=logging.DEBUG):
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def main():
    """
    pluperfect - Run per test case coverage and method parsing on a project for a set of commits.
    """
    init_logger()

    logging.info("Start analysis...")
    DB_PATH = ":memory:"

    arguments = parse_arguments()
    project_url = arguments.project_url
    config_path = arguments.config

    if config_path is not None:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())

        analysis_config = config["analysis"]
        output_path = f"{os.getcwd()}{os.path.sep}"
        DB_PATH = analysis_config["DB_LOCATION"]
        if analysis_config["OUTPUT_DIR"]:
            output_path = analysis_config["OUTPUT_DIR"]
        tacoco_path = analysis_config["TACOCO_HOME"]
        history_slider_path = analysis_config["HISTORY_SLICER_HOME"]
    else:
        logging.info("Provide config path...")
        exit(1)

    start(DB_PATH, project_url, output_path, tacoco_path, history_slider_path, arguments=arguments)
