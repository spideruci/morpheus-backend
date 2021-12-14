import logging
import json
import os
from pathlib import Path
from os.path import isdir, realpath, join, sep
from typing import Dict, List
from morpheus.analysis.parser.methods import MethodParser
from morpheus.analysis.parser.tacoco import TacocoParser
from morpheus.config import Config
from morpheus.database.models.repository import Project, Commit
from morpheus.database.db import create_engine_and_session, init_db

logger = logging.getLogger(__name__)

def get_directories(root_path) -> list[tuple[str, Path]]:
    projects = []

    # List all entries in directory
    for project in os.listdir(root_path):

        # resolve paths (allows us to include symlinks)
        real_project_path = realpath(join(root_path, project))

        # Check for each path if it is an directory
        if isdir(real_project_path):
            projects.append((project, Path(real_project_path)))

    return projects

def load_json(path) -> List[Dict]:
    with open(path) as f:
        return json.load(f)

def create_database(input_directory, database_path: Path, is_single_project: bool):

    # Update configuration
    if database_path is not None:
        Config.DATABASE_PATH = str(database_path.resolve())

    logger.debug("Database path: %s", Config.DATABASE_PATH)

    logger.info("Initialize database")
    (engine, Session) = create_engine_and_session()
    
    init_db(engine)

    # Check if input_directory exists and is a directory
    if not isdir(input_directory):
        logger.error("Input directory doesn't exist, %s", input_directory)
        return 1

    # Obtain all projects, except if path is for single project
    projects = [(os.path.basename(input_directory) , input_directory)]
    if not is_single_project:
        projects = get_directories(input_directory)

    if not projects:
        logger.error("No projects found in input directory")
        exit(1)
    else:
        logger.debug("Project(s) found: %s", projects)

    tacoco_parser = TacocoParser()
    method_parser = MethodParser()

    # Iterate over project and directory name tuple
    for (project_name, project_path) in projects:
        logger.info(f"Start storing project '{project_name}' in database.")

        # Store Project
        project_json = load_json( project_path / 'project.json')
        project = Project(**project_json)

        if Session.query(Project).filter(Project.project_name==project_name).first() is None:
            Session.add(project)
            Session.commit()

        for (commit_sha, commit_path) in get_directories(project_path):
            logger.info(f"Start storing commit '{commit_sha}' of project'{project_name}' in database.")

            # ToDo: Split parsing and storing into separate parts, if coverage doesn't exist, don't store the commit.

            # Store Commit
            commit_json = load_json(commit_path / 'commits.json')
            commit = Commit(**commit_json, project_id=project.id)

            if Session.query(Project).filter(Project.project_name==project_name).first() is None:
                logger.warning(f"SKIP - Commit '{commit_sha}' of project'{project_name}' is already in the database.")
                continue

            Session.add(commit)
            Session.commit()

            #  Parse Methods
            methods_json = load_json(commit_path / 'methods.json')

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

            # Clean up stored data to reduce memory consumption
            del methods_json
            del parsed_methods
            logger.info("\tFinished method storing")

            #  Parse Coverage.
            coverage_json = load_json(commit_path / 'coverage-cov-matrix.json')
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

            # Clean up stored data to reduce memory consumption
            del coverage_json
            del parsed_coverage
            logger.info("\tFinished Tacoco storing")

            