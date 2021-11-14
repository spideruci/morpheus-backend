import logging
from argparse import ArgumentParser
from morpheus.commands.analysis import run_analysis
from morpheus.commands.server import start_morpheus_backend
from morpheus.commands.db import create_database
from morpheus.commands.extract import extract_coverage

logger = logging.getLogger(__name__)

def init_logger(logging_level=logging.DEBUG):
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def create_argument_parser():
    """
    Parse arguments to run pluperfect.
    """
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    # -------------------------------------------
    #  Analysis CLI parser
    # -------------------------------------------
    analysis_parser = subparsers.add_parser("analyze", help="Obtain historical coverage data from repository.")
    analysis_parser.add_argument('url', type=str, help="Absolute path or url to system-under-test.")
    analysis_parser.add_argument('output_path', type=str, help="absolute path to output directory")

    commit_selection_group = analysis_parser.add_mutually_exclusive_group(required=True)
    commit_selection_group.add_argument('--current', action='store_true', help="Run the analysis on current version of the code")
    commit_selection_group.add_argument('--tags', type=int, help="Run the analysis on specified amount of tags, -1 would be all tags")
    commit_selection_group.add_argument('--commits', type=int, help="Run the analysis on specified amount of commits, -1 would be all commits")

    analysis_parser.set_defaults(func=morpheus_analysis)

    # -------------------------------------------
    #  Create database CLI parser
    # -------------------------------------------
    db_parser = subparsers.add_parser("db", help="Create database with morpheus coverage data.")
    db_parser.add_argument('input_folder', type=str, help='Directory of the data.')

    db_parser.set_defaults(func=morpheus_create_database)

    # -------------------------------------------
    #  Start server CLI parser
    # -------------------------------------------
    server_parser = subparsers.add_parser("server", help="Start server")
    server_parser.set_defaults(func=morpheus_start_backend)

    # -------------------------------------------
    #  Create static coverage CLI parser
    # -------------------------------------------
    json_parser = subparsers.add_parser("extract", help="Extract Morpheus coverage data from databse")
    json_parser.add_argument('output', type=str, help='Output directory.')

    json_parser.set_defaults(func=morpheus_extract_coverage)

    return parser

# -------------------------------------------
#  Subparser functions
# -------------------------------------------
def morpheus_analysis(args):
    try:
        run_analysis(args.url, args.output_path, args.current, args.tags, args.commits)
    except RuntimeError as e:
        logger.error("%s", e)


def morpheus_create_database(args):
    create_database(args.input_directory)

def morpheus_start_backend(args):
    start_morpheus_backend()

def morpheus_extract_coverage(args):
    extract_coverage(args.output)

# -------------------------------------------
#  Main program 
# -------------------------------------------
def main():
    init_logger()

    parser = create_argument_parser()

    args = parser.parse_args()

    args.func(args)

if __name__ == "__main__":
    main()