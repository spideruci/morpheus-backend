import docker

def main():
    # parse arguments
    #   - project url
    #   - database path
    #   - overwrite jdk?



    # Determine project type (gradle vs maven)


    # Create command


    # TODO: Pull docker image for jdk11 + maven
    # But for now use by default jdk_11_maven test.
    client = docker.from_env()

    docker_image_tag = 'jdk_11_maven'
    if docker_image_tag not in client.containers.list():
        client.pull(docker_image_tag)

    # Start docker image with database path volume
    client.containers.run(docker_image_tag, cmd)