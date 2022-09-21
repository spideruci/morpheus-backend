FROM python:3.10-alpine as BUILDER

RUN apk add --no-cache build-base git

WORKDIR /usr/app/morpheus
COPY src/morpheus ./src/morpheus
COPY setup.py .
RUN python -m pip install --no-cache-dir .

CMD [ "matrix", "server", "--port", "8080", "--host", "0.0.0.0", "/srv/morpheus/jpacman-framework-commits.sqlite" ]