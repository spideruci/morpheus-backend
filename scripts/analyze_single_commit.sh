#!/bin/bash
set -euxo pipefail

. ./venv/bin/activate 

IDENTIFIER=20211218
COV=coverage
DB=databases
STATIC=static

HOME_DIR=/srv/research/tacoco_verify
COVERAGE_DIR=$HOME_DIR/$COV
DATABASE_DIR=$HOME_DIR/$DB/$IDENTIFIER
STATIC_DIR=$HOME_DIR/$STATIC/$IDENTIFIER

project=jpacman-framework

# Make sure the output directories exists.
mkdir -p "$COVERAGE_DIR"
mkdir -p "$DATABASE_DIR"
mkdir -p "$STATIC_DIR"

trap "kill 0" EXIT

for i in $(seq 1 10);
do
	project_id="$project-$i"
	echo "PROJECT: $project_id"
	matrix analyze https://github.com/SERG-DELFT/jpacman-framework $COVERAGE_DIR/$project_id --tags 5
	matrix db --project "$COVERAGE_DIR/$project_id/$project" "$DATABASE_DIR/$project_id.sqlite"
       	matrix extract "$DATABASE_DIR/$project_id.sqlite" "$STATIC_DIR/$project_id"
done

