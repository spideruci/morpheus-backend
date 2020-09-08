import tarfile
import docker
import logging
from spidertools.utils.analysis_repo import AnalysisRepo
import xml


def get_jdk_version(repo: AnalysisRepo):
    return str(11)

def create_archive(directory):
    pass

def main():
    # parse arguments
    #   - project url
    #   - database path
    #   - overwrite jdk?

    url = 'https://github.com/apache/commons-io'

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
    client = docker.from_env()

    try: 
        client.images.get(docker_image_tag)
    except Exception:
        print(f"[ERROR] Docker image '{docker_image_tag}' was not found...")
        exit(1)

    # Build command
    cmd = [
        "pluperfect",
        url,
        "--config .spider.yml"
    ]

    print(f"[INFO] cmd: {' '.join(cmd)}")

    # Start docker image with database path volume
    client.containers.run(docker_image_tag, ' '.join(cmd), stderr=True)