#!/bin/bash
set -euxo pipefail

. ./venv/bin/activate 

IDENTIFIER=20220102
COV=coverage
DB=databases
STATIC=static

HOME_DIR=/srv/research/morpheus
COVERAGE_DIR=$HOME_DIR/$COV
DATABASE_DIR=$HOME_DIR/$DB/$IDENTIFIER
STATIC_DIR=$HOME_DIR/$STATIC/$IDENTIFIER

projects=(
	"$1"
)

# Make sure the output directories exists.
mkdir -p "$COVERAGE_DIR"
mkdir -p "$DATABASE_DIR"
mkdir -p "$STATIC_DIR"

trap "kill 0" EXIT

for project in ${projects[@]};
do
   matrix db --project "$COVERAGE_DIR/$project" "$DATABASE_DIR/$project.sqlite"  & 
done

wait
