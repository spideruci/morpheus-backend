import argparse
import os
import yaml
from spidertools.utils.git_repo import GitRepo
from spidertools.tools.tacoco import TacocoRunner
from spidertools.tools.history import HistoryRunner, MethodParserRunner
from spidertools.process_data.coverage_json import coverage_json
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
    with GitRepo(project_url) as repo:
        tacoco_runner = TacocoRunner(repo, output_path, tacoco_path)
        parser_runner = MethodParserRunner(repo, output_path, history_slider_path)

        for commit in repo.iterate_tagged_commits(5):
            print(commit, repo.get_current_commit())

            # Before each analysis remove all generated files of previous run
            repo.clean()

            # Start analysis
            build_output = tacoco_runner.build()

            if build_output == 1:
                print("[ERROR] build failure...")
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

def main():
    print("Start analysis...")
    arguments = parse_arguments()
    project_url = arguments.project_url
    config_path = arguments.config
    
    if config_path is not None:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())
        output_path = config["OUTPUT_DIR"]
        tacoco_path = config["TACOCO_HOME"]
        history_slider_path = config["HISTORY_SLICER_HOME"]

    start(project_url, output_path, tacoco_path, history_slider_path)
