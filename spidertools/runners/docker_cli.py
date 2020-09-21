import argparse
import tarfile
import docker
import logging
import os
from spidertools.utils.analysis_repo import AnalysisRepo
import xml
from io import BytesIO
from typing import Dict, Tuple, List



def get_jdk_version(repo: AnalysisRepo):
    return str(11)

def create_archive(repo: AnalysisRepo):
    """
    
    """
    file_out = BytesIO()
    
    with tarfile.open(fileobj=file_out, mode="w:gz") as tar:
        source_dir = repo.get_project_directory()
        tar.add(source_dir, arcname=repo.get_project_name())

    return file_out.getvalue()

def parse_arguments():
    """
    Parse arguments to run experiment in docker container.
    """
    parser = argparse.ArgumentParser(description="Tool to run the spidertools analysis framework in a docker container")

    parser.add_argument('project_url', type=str, help="URL to a git repository that can be cloned for analysis")
    parser.add_argument('output_dir', type=str, help="Directory where the user wants to store the output from the analysis")
    
    return parser.parse_args()

def create_volume(host_dir: str):
    if host_dir is None:
        raise Exception("Host or docker target directory is undefined...")

    return [host_dir], {
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

    with AnalysisRepo(url) as repo:
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
            docker_client = docker.from_env()
        except Exception:
            print(f"[ERROR] Docker is not installed or not running at the moment...")
            exit(1)

        try: 
            docker_client.images.get(docker_image_tag)
        except Exception:
            print(f"[ERROR] Docker image '{docker_image_tag}' was not found...")
            exit(1)

        # Create archive of a single snapshot and place it in the container
        file_out = BytesIO()
        repo.archive(file_out)

        # Build command
        cmd = [
            "pluperfect",
            f"/home/spiderlab/{repo.get_project_name()}",
            '--current',
            "--config .spider.yml"
        ]

        print(f"[INFO] cmd: {' '.join(cmd)}")

        cli = docker.APIClient(base_url='unix://var/run/docker.sock')

        volume, volume_bindings = create_volume(output_dir)

        host_config = cli.create_host_config(
            binds=volume_bindings
        )

        container = cli.create_container(
            image=docker_image_tag, 
            command=' '.join(cmd),
            volumes=volume,
            host_config=host_config
        )

        cli.put_archive(
            container=container.get('Id'),
            path="/home/spiderlab/",
            data=create_archive(repo)
        )

        cli.start(container=container.get('Id'))
        cli.wait(container=container.get('Id'))
    
        print(cli.logs(
            container=container.get('Id'),
            stdout=True,
            stderr=True
        ).decode('utf8'))
