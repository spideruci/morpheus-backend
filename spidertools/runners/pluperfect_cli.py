import argparse
import os
import yaml
from spidertools.utils.git_repo import GitRepo
from spidertools.tools.tacoco import TacocoRunner
from spidertools.tools.history import HistoryRunner, MethodParserRunner
from spidertools.process_data.coverage_json import coverage_json
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, BuildTableHandler

def parse_arguments():
    """
    Parse arguments to run Tacoco
    """
    parser = argparse.ArgumentParser(description='Run Tacoco')

    parser.add_argument('project_url', type=str,
                        help="Absolute path to system-under-test's root.")

    parser.add_argument('--output_path', type=str, help="absolute path to output directory")
    parser.add_argument('--config', type=str, help="absolute path to tacoco")

    return parser.parse_args()

def start(project_url, output_path, tacoco_path, history_slider_path, db_location: str):

    project_handler = ProjectTableHandler(db_location)
    commit_handler = CommitTableHandler(db_location)
    build_hanlder = BuildTableHandler(db_location)

    with GitRepo(project_url) as repo:
        # Add project and commit to database
        project_handler.add_project(repo.get_project_name())
        commit_handler.add_commit(project_handler.get_project_id(), repo.get_current_commit())


        # Analysis tools
        tacoco_runner = TacocoRunner(repo, output_path, tacoco_path)
        parser_runner = MethodParserRunner(repo, output_path, history_slider_path)

        build_output = tacoco_runner.build()

        build_hanlder.add_build_result()
        if build_output == 1:
            print("[ERROR] build failure...")
        else:
            parser_runner.run()
            tacoco_runner.run()

            # Combine data
            commit_sha = repo.get_current_commit()
            project_output_path = f"{output_path}{os.path.sep}{repo.get_project_name()}{os.path.sep}"
            output = coverage_json(
                f"{project_output_path}methods-{commit_sha}.json",
                f"{project_output_path}{commit_sha}-cov-matrix.json",
                f"{project_output_path}{commit_sha}-combined.json",
                commit_sha
            )



def main():
    print("Start analysis...")
    arguments = parse_arguments()
    project_url = arguments.project_url
    config_path = arguments.config
    
    if config_path is not None:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())
        output_path = config["OUTPUT_DIR"]
        db_path = config["DB_LOCATION"]
        tacoco_path = config["TACOCO_HOME"]
        history_slider_path = config["HISTORY_SLICER_HOME"]

    start(project_url, output_path, tacoco_path, history_slider_path, db_path)
