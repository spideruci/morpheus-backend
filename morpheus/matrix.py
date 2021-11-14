import logging
from pathlib import Path
from argparse import ArgumentParser
from morpheus.commands.analysis import run_analysis
from morpheus.commands.server import start_morpheus_backend
from morpheus.commands.db import create_database
from morpheus.commands.extract import extract_coverage
from ipaddress import IPv4Address, ip_address

logger = logging.getLogger(__name__)

def init_logger(logging_level=logging.DEBUG):
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def parse_arguments():
    """
    Parse arguments to run pluperfect.
    """
    parser = ArgumentParser(prog="Matrix", description="Collection of tools used to analyze, store, and serve the historical coverage data for the morpheus visualization.")
    subparsers = parser.add_subparsers()
    # -------------------------------------------
    #  Analysis CLI parser
    # -------------------------------------------
    analysis_parser = subparsers.add_parser("analyze", help="Obtain historical coverage data from repository.")
    analysis_parser.add_argument('url', type=str, help="URL or path to repository of system-under-test.")
    analysis_parser.add_argument('output', type=Path, help="Path to output directory")

    commit_selection_group = analysis_parser.add_mutually_exclusive_group(required=True)
    commit_selection_group.add_argument('--current', action='store_true', help="Run the analysis on current version of the code")
    commit_selection_group.add_argument('--tags', type=int, help="Run the analysis on specified amount of tags, -1 would be all tags")
    commit_selection_group.add_argument('--commits', type=int, help="Run the analysis on specified amount of commits, -1 would be all commits")

    analysis_parser.set_defaults(func=morpheus_analysis)

    # -------------------------------------------
    #  Create database CLI parser
    # -------------------------------------------
    db_parser = subparsers.add_parser("db", help="Create database with morpheus coverage data.")
    db_parser.add_argument('input_folder', type=Path, help='Directory of the data.')
    db_parser.add_argument('-o', '--output', type=Path, help="Database location")

    db_parser.set_defaults(func=morpheus_create_database)

    # -------------------------------------------
    #  Start server CLI parser
    # -------------------------------------------
    server_parser = subparsers.add_parser("server", help="Start server")
    server_parser.add_argument('database', type=Path, help="path to database")
    server_parser.add_argument('--host', type=ip_address, default=IPv4Address('127.0.0.1'), help='Port of the tool')
    server_parser.add_argument('-p', '--port', type=int, default=8080, help='Port of the tool')
    server_parser.add_argument('-d', '--debug', action='store_true', help='Port of the tool')
    server_parser.set_defaults(func=morpheus_start_backend)

    # -------------------------------------------
    #  Create static coverage CLI parser
    # -------------------------------------------
    json_parser = subparsers.add_parser("extract", help="Extract Morpheus coverage data from databse")
    json_parser.add_argument('database', type=Path, help='Path to database.')
    json_parser.add_argument('output', type=Path, help='Output directory.')
    json_parser.set_defaults(func=morpheus_extract_coverage)

    return parser.parse_args()

# -------------------------------------------
#  Subparser command functions
# -------------------------------------------
def morpheus_analysis(args):
    try:
        run_analysis(args.url, args.output, args.current, args.tags, args.commits)
    except RuntimeError as e:
        logger.error("%s", e)


def morpheus_create_database(args):
    create_database(args.input_folder, args.output)

def morpheus_start_backend(args):
    start_morpheus_backend(args.database, args.host, args.port, args.debug)

def morpheus_extract_coverage(args):
    extract_coverage(args.database, args.output)

# -------------------------------------------
#  Main program 
# -------------------------------------------
def main():
    args = parse_arguments()

    init_logger()

    args.func(args)

if __name__ == "__main__":
    main()