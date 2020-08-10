import argparse
import os
import yaml
from spidertools.utils.analysis_repo import AnalysisRepo
from spidertools.tools.tacoco import TacocoRunner

def parse_arguments():
    """
    Parse arguments to run Tacoco
    """
    parser = argparse.ArgumentParser(description='Run Tacoco')

    parser.add_argument('project_url', type=str,
                        help="Absolute path to system-under-test's root.")

    parser.add_argument('--output_path', type=str, help="absolute path to output directory")
    parser.add_argument('--tacoco_path', type=str, help="absolute path to tacoco")
    parser.add_argument('--config', type=str, help="absolute path to tacoco")

    return parser.parse_args()

def start(project_url, output_path, tacoco_path):
    with AnalysisRepo(project_url).set_depth(1) as repo:
        runner = TacocoRunner(repo, output_path, tacoco_path)

        build_output = runner.build()

        if build_output == 1:
            print("[ERROR] build failure...")
        else:
            runner.run()



def main():
    print("Start analysis...")
    arguments = parse_arguments()
    project_url = arguments.project_url
    output_path = arguments.output_path
    tacoco_path = arguments.tacoco_path
    config_path = arguments.config

    if (output_path is None and tacoco_path is None) and (config_path is None):
        exit(1)
    
    if config_path is not None:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())
        output_path = config["OUTPUT_DIR"]
        tacoco_path = config["TACOCO_HOME"]

    start(project_url, output_path, tacoco_path)
