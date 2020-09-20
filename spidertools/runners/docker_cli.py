import argparse
import tarfile
import docker
import logging
from spidertools.utils.analysis_repo import AnalysisRepo
import xml
from typing import Dict


def get_jdk_version(repo: AnalysisRepo):
    return str(11)

def create_archive(directory):
    pass

def parse_arguments():
    """
    Parse arguments to run experiment in docker container.
    """
    parser = argparse.ArgumentParser(description="Tool to run the spidertools analysis framework in a docker container")

    parser.add_argument('project_url', type=str, help="URL to a git repository that can be cloned for analysis")
    parser.add_argument('output_dir', type=str, help="Directory where the user wants to store the output from the analysis")
    
    return parser.parse_args()

def create_volume(host_dir: str) -> Dict:
    if host_dir is None:
        raise Exception("Host or docker target directory is undefined...")

    return {
        host_dir: {
            'bind': "/home/spiderlab/data/",
            'mode': 'rw'
        }
    }

def main():
    # parse arguments
    #   - project url
    #   - database path
    args = parse_arguments()
    url = args.project_url
    output_dir = args.output_dir

    repo = AnalysisRepo(url)

    with repo as repo:
        directory = repo.get_project_directory()

    # Get JDK version
    jdk_version = get_jdk_version(repo)

    map_jdk_to_image = {
        "13" : 'spider-jdk-13',
        "11" : 'spider-jdk-11',
        "8" : 'spider-jdk-8'
    }

    docker_image_tag = map_jdk_to_image[jdk_version]

    # Make connection with the docker deamon 
    try: 
        client = docker.from_env()
    except Exception:
        print(f"[ERROR] Docker is not installed or not running at the moment...")
        exit(1)

    try: 
        client.images.get(docker_image_tag)
    except Exception:
        print(f"[ERROR] Docker image '{docker_image_tag}' was not found...")
        exit(1)

    # Create volume to use with the docker container:
    volume = create_volume(output_dir)

    # Build command
    cmd = [
        "pluperfect",
        url,
        '--current',
        "--config .spider.yml"
    ]

    print(f"[INFO] cmd: {' '.join(cmd)}")

    # Start docker image with database path volume
    client.containers.run(docker_image_tag, ' '.join(cmd), volumes=volume, stderr=True)