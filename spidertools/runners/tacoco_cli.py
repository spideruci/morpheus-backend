import argparse
import os
import yaml
from spidertools.utils.git_repo import GitRepo
from spidertools.tools.tacoco import TacocoRunner

def parse_arguments():
    """
    Parse arguments to run Tacoco
    """
    parser = argparse.ArgumentParser(description='Run Tacoco')

    parser.add_argument('project_url', type=str,
                        help="Absolute path to system-under-test's root.")

    parser.add_argument('project_path', type=str, help="")
    parser.add_argument('--output_path', type=str, help="absolute path to output directory")
    parser.add_argument('--tacoco_path', type=str, help="absolute path to tacoco")
    parser.add_argument('--config', type=str, help="absolute path to tacoco")

    return parser.parse_args()

def start(project_url, project_path, output_path, tacoco_path):
    with GitRepo(project_url, project_path).set_depth(1).clone() as repo:
        runner = TacocoRunner(repo, output_path, tacoco_path)

        build_output = runner.build()

        if build_output == 0:
            runner.run()

        print("[ERROR] build failure...")

def main():
    print("Start analysis...")
    arguments = parse_arguments()
    project_url = arguments.project_url
    project_path = arguments.project_path
    output_path = arguments.output_path
    tacoco_path = arguments.tacoco_path
    config_path = arguments.config

    if (output_path is None and tacoco_path is None) and (config_path is None):
        exit(1)
    
    if config_path is not None:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())
        tacoco_path = config["TACOCO_HOME"]
        output_path = config["OUTPUT_DIR"]

    start(project_url, project_path, output_path, tacoco_path)
