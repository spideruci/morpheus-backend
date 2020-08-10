import argparse
import os
import yaml
import json
from spidertools.utils.git_repo import AnalysisRepo
from spidertools.tools.tacoco import TacocoRunner
from spidertools.tools.history import MethodParserRunner
from spidertools.process_data.coverage_json import coverage_json
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler

# By default the database is only created in memory
DB_PATH = ":memory:"

def parse_arguments():
    """
    Parse arguments to run Tacoco
    """
    parser = argparse.ArgumentParser(description='Run Tacoco')

    # TODO: Add option to switch between number of releases and number of commits
    parser.add_argument('project_url', type=str,
                        help="Absolute path to system-under-test's root.")
    parser.add_argument('--output_path', type=str, help="absolute path to output directory")
    parser.add_argument('--config', type=str, help="absolute path to tacoco")

    return parser.parse_args()

def start(project_url, output_path, tacoco_path, history_slider_path):
    global DB_PATH

    project_handler = ProjectTableHandler(DB_PATH)
    commit_handler = CommitTableHandler(DB_PATH)
    coverage_handler = MethodCoverageHandler(DB_PATH)

    with AnalysisRepo(project_url) as repo:
        # Add project and commit to database
        if (project_id := project_handler.get_project_id(repo.get_project_name())) is None:
            project_id = project_handler.add_project(repo.get_project_name())

        # Analysis tools
        tacoco_runner = TacocoRunner(repo, output_path, tacoco_path)
        parser_runner = MethodParserRunner(repo, output_path, history_slider_path)

        for commit in repo.iterate_tagged_commits(5):
            commit_id = commit_handler.get_commit_id(project_id, commit)

            if commit_id is not None:
                print(f'[Warning] commit ID already exists: {commit}')
                continue
            else:
                print(f'[Info] commit ID does not exist yet: {commit}')

            commit_id = commit_handler.add_commit(project_id, commit)

            output = _analysis(repo, tacoco_runner, parser_runner, output_path)

            if output:
                project_output_path = f"{output_path}{os.path.sep}{repo.get_project_name()}{os.path.sep}"
                commit_sha = repo.get_current_commit()
                with open(f"{project_output_path}{commit_sha}-combined.json") as f:
                    data = json.load(f)
                    coverage_handler.add_project_coverage(project_id, commit_id, data["methods"]["production"], data["methods"]["test"])



def _analysis(repo, tacoco_runner, parser_runner, output_path):
    # Before each analysis remove all generated files of previous run
    repo.clean()

    # Start analysis
    build_output = tacoco_runner.build()

    if build_output == 1:
        print("[ERROR] build failure...")
        return False
    else:
        parser_runner.run()
        tacoco_runner.run()

        # Combine data
        commit_sha = repo.get_current_commit()
        commit_id = commit_sha
        project_output_path = f"{output_path}{os.path.sep}{repo.get_project_name()}{os.path.sep}"
        coverage_json(
            f"{project_output_path}methods-{commit_sha}.json",
            f"{project_output_path}{commit_sha}-cov-matrix.json",
            f"{project_output_path}{commit_sha}-combined.json",
            commit_id
        )

        return True

def main():
    print("Start analysis...")
    global DB_PATH

    arguments = parse_arguments()
    project_url = arguments.project_url
    config_path = arguments.config
    
    if config_path is not None:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())

        output_path = config["OUTPUT_DIR"]
        DB_PATH = config["DB_LOCATION"]
        if config["OUTPUT_DIR"]:
            output_path = config["OUTPUT_DIR"]
        tacoco_path = config["TACOCO_HOME"]
        history_slider_path = config["HISTORY_SLICER_HOME"]

    start(project_url, output_path, tacoco_path, history_slider_path)
