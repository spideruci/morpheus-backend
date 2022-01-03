import logging
import json
import os
from pathlib import Path
from os.path import isdir, realpath, join, sep
from typing import Dict, List
from tqdm import tqdm
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
        if isdir(real_project_path) and 'logs' not in real_project_path:
            projects.append((project, Path(real_project_path)))

    return projects

def load_json(path):
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

    # Iterate over project and directory name tuple
    for (project_name, project_path) in tqdm(projects):
        logger.info(f"Start storing project '{project_name}' in database.")

        # Store Project
        project_json = load_json( project_path / 'project.json')
        project = Project(**project_json)

        if Session.query(Project).filter(Project.project_name==project_name).first() is None:
            Session.add(project)
            Session.commit()

        for (commit_sha, commit_path) in tqdm(get_directories(project_path)):
            try:
                analyze_commit(Session, project, commit_sha, commit_path)
            except:
                logger.error("Failed to store commit %s in database", commit_sha)
                continue


def analyze_commit(Session, project: Project, commit_sha: str, commit_path: Path):
    logger.info(f"Start storing commit '{commit_sha}'/{commit_path}")

    # Store Commit
    commit_json = load_json(commit_path / 'commits.json')
    commit = Commit(**commit_json, project_id=project.id)

    Session.add(commit)
    Session.commit()

    parsed_methods = []
    parsed_coverage = []
    
    #  Parse Methods
    try:
        methods_file = commit_path / 'methods.json'
        tacoco_file = commit_path / 'coverage-cov-matrix.json'

        logger.debug("Parse methods/tacoco json: %s %s", methods_file, tacoco_file)

        methods_json = load_json(methods_file)
        parsed_methods = MethodParser()\
            .parse(methods_json)

        coverage_json = load_json(tacoco_file)
        parsed_coverage =  TacocoParser()\
            .parse(coverage_json)

    except RuntimeError:
        logger.critical("Failing to parse tacoco/methods file - commit: %s", commit.id)
        Session.delete(commit)
        Session.flush()
        raise

    #  Parse Coverage.
    try:
        MethodParser().store(
            session=Session,
            project=project,
            commit=commit,
            methods=parsed_methods
        )

        TacocoParser().store(
            session=Session,
            project=project,
            commit=commit,
            coverage=parsed_coverage
        )
    except RuntimeError as exc:
        logger.critical("Failed to store data in database - commit: %s, Exception: %s", commit.id, exc)
        Session.delete(commit)
        Session.flush()
        raise
