#!/bin/bash
set -euxo pipefail

. ./venv/bin/activate 

IDENTIFIER=20211218
COV=coverage2
DB=databases
STATIC=static

HOME_DIR=/srv/research/morpheus
COVERAGE_DIR=$HOME_DIR/$COV
DATABASE_DIR=$HOME_DIR/$DB/$IDENTIFIER
STATIC_DIR=$HOME_DIR/$STATIC/$IDENTIFIER

project_url=https://github.com/serg-delft/jpacman-framework
project=jpacman-framework

# Make sure the output directories exists.
mkdir -p "$COVERAGE_DIR"
mkdir -p "$DATABASE_DIR"
mkdir -p "$STATIC_DIR"

trap "kill 0" EXIT

matrix analyze "$project_url" $COVERAGE_DIR --commits -1
matrix db --project "$COVERAGE_DIR/$project" "$DATABASE_DIR/$project.sqlite"
matrix extract "$DATABASE_DIR/$project.sqlite" "$STATIC_DIR/$project"

