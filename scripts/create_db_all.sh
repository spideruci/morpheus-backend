#!/bin/bash
set -euxo pipefail

. ./venv/bin/activate 

IDENTIFIER=$(date '+%Y%m%d-%H%M')
COV=coverage
DB=databases
STATIC=static
LOGS=logs

HOME_DIR=/srv/research/morpheus
OUTPUT_DIR=$HOME_DIR/out/$IDENTIFIER

COVERAGE_DIR=$HOME_DIR/$COV

LOG_DIR=$OUTPUT_DIR/$LOGS
STATIC_DIR=$OUTPUT_DIR/$STATIC

DATABASE_DIR=$OUTPUT_DIR/$DB
DATABASE_PATH=$DATABASE_DIR/combined.sqlite

projects=(
	"commons-cli"
	"commons-configuration"
	"commons-csv"
	"commons-imaging"
	"commons-io"
	"commons-jexl"
	"commons-lang"
	"commons-net"
	"commons-pool"
	"commons-text"
	"commons-validator"
	"commons-vfs"
	"error-prone"
	"re2j"
	"truth"
	"jsoup"
	"dubbo"
	"google-java-format"
	"gson"
	"iotdb"
	"junit4"
	"maven"
	"xmlgraphics-commons"
	"zookeeper"
	"itext7"
	"fastjson"
)

echo ${projects[@]}

# Make sure the output directories exists.
mkdir -p "$OUTPUT_DIR"
mkdir -p "$COVERAGE_DIR"
mkdir -p "$DATABASE_DIR"
mkdir -p "$STATIC_DIR"
mkdir -p "$LOG_DIR"

trap "kill 0" EXIT

for project in ${projects[@]};
do
   matrix db --project "$COVERAGE_DIR/$project" "$DATABASE_PATH" > "$LOG_DIR/$project-db.logs" 2>&1
done

matrix extract "$DATABASE_PATH" "$STATIC_DIR" > "$LOG_DIR/extract.logs" 2>&1

