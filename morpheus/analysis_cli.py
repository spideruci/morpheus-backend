from argparse import ArgumentParser
import os
import logging
import json
from typing import Tuple, List
from morpheus.analysis.util.subject import AnalysisRepo
from morpheus.analysis.tacoco import TacocoRunner
from morpheus.analysis.methodsignature import MethodParserRunner
from morpheus.database.models.repository import Commit, Project
from morpheus.config import Config
from morpheus.database.util import row2dict
from os.path import sep

logger = logging.getLogger(__name__)

def init_logger(logging_level=logging.DEBUG):
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def parse_arguments():
    """
    Parse arguments to run pluperfect.
    """
    parser = ArgumentParser(description='Run Tacoco')

    parser.add_argument('project_url', type=str, help="Absolute path or url to system-under-test.")
    parser.add_argument('output_path', type=str, help="absolute path to output directory")

    commit_selection_group = parser.add_mutually_exclusive_group(required=True)
    commit_selection_group.add_argument('--current', action='store_true', help="Run the analysis on current version of the code")
    commit_selection_group.add_argument('--tags', type=int, help="Run the analysis on specified amount of tags, -1 would be all tags")
    commit_selection_group.add_argument('--commits', type=int, help="Run the analysis on specified amount of commits, -1 would be all commits")

    return parser.parse_args()

def run_analysis(arguments):

    project_url = arguments.project_url
    output_path = arguments.output_path

    if not os.path.exists(output_path):
        logger.warning(f'Output path did not exists: {output_path}, so it was created.')
        os.makedirs(output_path)

    with AnalysisRepo(project_url) as repo:
        logger.info("Project: %s", repo.get_project_name())

        # Add project
        project = Project(project_name=repo.get_project_name())

        if not os.path.exists(f"{output_path}{os.path.sep}{repo.get_project_name()}"):
            os.makedirs(f"{output_path}{os.path.sep}{repo.get_project_name()}")
        with open(f"{output_path}{os.path.sep}{repo.get_project_name()}{sep}project.json", 'w') as f:
            f.write(json.dumps(row2dict(project)))


        if Config.TACOCO_HOME is None or Config.PARSER_HOME is None:
            logger.error("Please provide root folder of TACOCO and/or the Method Parser.")
            exit(1)

        # Analysis tools
        tacoco_runner = TacocoRunner(repo, output_path, Config.TACOCO_HOME)
        parser_runner = MethodParserRunner(repo, output_path, Config.PARSER_HOME)

        # Get all commits we want to run the analysis on.
        commits: List[Commit] = []
        if arguments.current:
            commits = [repo.get_current_commit()]
        elif arguments.tags is not None:
            commits = repo.iterate_tagged_commits(arguments.tags)
        elif arguments.commits is not None:
            commits = repo.iterate_commits(arguments.commits)
        else:
            logger.error("The run was misconfigured...")
            exit(0)
        
        for commit in commits:
            logger.info("[INFO] Analyze commit: %s", commit.sha)

            # Run analysis and return paths to output files
            success, method_file_path, tacoco_file_path = _analysis(repo, tacoco_runner, parser_runner, output_path)
            
            if not success:
                logger.error('Analysis for %s failed...', commit.sha)
                continue
            else:
                logger.info(f'Output per file: \n\tMethod File: {method_file_path}\n\tTacoco File: {tacoco_file_path}')

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
    commit: Commit = repo.get_current_commit()

    with open(f"{output_path}{os.path.sep}{repo.get_project_name()}{sep}{commit.sha}{sep}commit.json", 'w') as f:
            f.write(json.dumps(row2dict(commit)))

    logger.info("build successfull...")
    return (True,
        f"methods.json",
        f"coverage.json"
    )

def main():
    """
    pluperfect - Run per test case coverage and method parsing on a project for a set of commits.
    """
    logger.info("Start analysis...")
    init_logger()

    arguments = parse_arguments()

    run_analysis(arguments=arguments)
