#!/bin/sh

ORG_NAME=kajdreef
IMAGE=morpheus-backend
PLATFORMS=linux/amd64,linux/arm64

DOCKER_IMG="$ORG_NAME/$IMAGE"

docker_build() {
    
    echo "Build docker image: $DOCKER_IMG"

    VERSION=local
    echo docker build . -t "$DOCKER_IMG:$VERSION"
    docker build . -t "$DOCKER_IMG:$VERSION"
}

docker_buildx() {
    
    echo "Build docker image: $DOCKER_IMG"

    if [ "$1" -eq 1 ];
    then
        VERSION=latest
        echo docker buildx build --platform $PLATFORMS -t "$DOCKER_IMG:$VERSION" . --push
        docker buildx build --platform $PLATFORMS -t "$DOCKER_IMG:$VERSION" . --push
    else
        VERSION=unstable
        echo docker buildx build --platform $PLATFORMS -t "$DOCKER_IMG:$VERSION" . --push
        docker buildx build --platform $PLATFORMS -t "$DOCKER_IMG:$VERSION" . --push
    fi
}

docker_run() {
    VERSION=local

    # Delete the unstable local and pull latest unstable image.
    docker rmi "$DOCKER_IMG"

    echo Run docker image: "$DOCKER_IMG:$VERSION"
    echo docker run "$DOCKER_IMG:$VERSION" /bin/sh
    docker run -p 5000:5000 -it "$DOCKER_IMG:$VERSION" /bin/sh
}

docker_lint() {
    docker run --rm -i hadolint/hadolint < Dockerfile
}

while getopts "rbxpl" flag; do
    case "$flag" in
        r)
            docker_run
            exit 0
            ;;
        b)
            docker_build
            exit 0
            ;;
        x)
            docker_buildx 0
            exit 0
            ;;
        p)
            docker_buildx 1
            exit 0
            ;;
        l)
            docker_lint
            exit 0
            ;;
        *)
            exit 1
            ;;
    esac
done
