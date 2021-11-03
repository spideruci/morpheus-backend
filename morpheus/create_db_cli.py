import logging
import json
import os
from argparse import ArgumentParser
from os.path import isdir, join, sep
from morpheus.analysis.parser.methods import MethodParser
from morpheus.analysis.parser.tacoco import TacocoParser
from morpheus.database.models.repository import Project, Commit
from morpheus.database.db import Session, engine, init_db

logger = logging.getLogger(__name__)

def init_logger(logging_level=logging.DEBUG):
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def parse_arguments():
    parser = ArgumentParser(description='Create morpheus database')

    parser.add_argument('input_folder', type=str, help='Directory of the data.')
    
    return parser.parse_args()

def get_directories(root_path):
    return [project for project in os.listdir(root_path) if isdir(join(root_path, project))]

def load_json(path):
    with open(path) as f:
        return json.load(f)

def main():
    init_logger()

    arguments = parse_arguments()
    
    input_directory = arguments.input_folder

    logger.info("Initialize database")
    init_db(engine)

    # Obtain all projects
    projects = []
    if not isdir(input_directory):
        logger.error("Input directory doesn't exist")
        return 1

    projects = get_directories(input_directory)

    tacoco_parser = TacocoParser()
    method_parser = MethodParser()

    for project_name in projects:
        logger.info(f"Start storing project '{project_name}' in database.")

        # Store Project
        project_json = load_json(f'{input_directory}{sep}{project_name}{sep}project.json')
        project = Project(**project_json)

        if Session.query(Project).filter(Project.project_name==project_name).first() is None:
            Session.add(project)
            Session.commit()

        for commit_sha in get_directories(f'{input_directory}{sep}{project_name}'):

            logger.info(f"Start storing commit '{commit_sha}' of project'{project_name}' in database.")

            # ToDo: Split parsing and storing into separate parts, if coverage doesn't exist, don't store the commit.

            # Store Commit
            commit_json = load_json(f'{input_directory}{sep}{project_name}{sep}{commit_sha}{sep}commit.json')
            commit = Commit(**commit_json, project_id=project.id)

            if Session.query(Project).filter(Project.project_name==project_name).first() is None:
                logger.warning(f"SKIP - Commit '{commit_sha}' of project'{project_name}' is already in the database.")
                continue

            Session.add(commit)
            Session.commit()

            #  Parse Methods
            methods_json = load_json(f'{input_directory}{sep}{project_name}{sep}{commit_sha}{sep}methods.json')

            parsed_methods = method_parser\
                .set_commit(commit) \
                .parse(methods_json)
            
            logger.info("Start method storing, total: %s", len(parsed_methods))
            method_parser.store(
                session=Session,
                project=project,
                commit=commit,
                methods=parsed_methods
            )
            logger.info("\tFinished method storing")

            #  Parse Coverage.
            coverage_json = load_json(f'{input_directory}{sep}{project_name}{sep}{commit_sha}{sep}coverage-cov-matrix.json')
            parsed_coverage = tacoco_parser\
                .parse(coverage_json)
            
            logger.debug('Number of testcases: %s', len(parsed_coverage))

            logger.info("Start Tacoco storing")
            tacoco_parser.store(
                session=Session,
                project=project,
                commit=commit,
                coverage=parsed_coverage
            )
            logger.info("\tFinished Tacoco storing")

            