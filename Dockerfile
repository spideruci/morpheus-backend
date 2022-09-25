FROM python:3.10-alpine as BUILDER

# Install tools needed to install application
RUN apk add --no-cache build-base git

# Install application:
WORKDIR /usr/app/morpheus
COPY src/morpheus ./src/morpheus
COPY setup.py .
RUN python -m pip install --no-cache-dir .

# Setup gunicorn configurations
WORKDIR /etc/gunicorn/
COPY resources/gunicorn_config.py .

WORKDIR /usr/app/morpheus
# Run backend using gunicorn.
CMD [ "gunicorn", "--config", "/etc/gunicorn/gunicorn_config.py", "morpheus.commands.server:start_gunicorn('/srv/morpheus/coverage.sqlite')" ]