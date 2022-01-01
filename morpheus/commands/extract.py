import logging
from multiprocessing import Pool
from typing import Dict, List
from morpheus.api.endpoints.project_routes import ProjectsRoute, CommitsRoute
from morpheus.api.endpoints.methods_routes import MethodsInProjectRoute
from morpheus.api.endpoints.tests_routes import TestMethodsInCommitRoute
from morpheus.api.endpoints.coverage_routes import MethodTestCoverageRoute, ProdMethodHistoryRoute, TestMethodHistoryRoute
from morpheus.config import Config
from morpheus.database.db import create_engine_and_session, init_db
from functools import wraps
from time import time
import json
from pathlib import Path
import os
from tqdm import tqdm

logger = logging.getLogger(__name__)


def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        time_start = time()
        result = f(*args, **kw)
        time_end = time()
        diff = time_end - time_start
        logger.debug("func:%s: %s sec", f.__name__, diff)
        return result
    return wrap


@timeit
def get_commit_coverage(project_id: int, base_dir: Path):
    commit_route = CommitsRoute()
    coverage = MethodTestCoverageRoute()

    commit_list_dir = base_dir / 'projects' / f'{project_id}'
    commit_coverage_dir = base_dir / 'coverage'  / f'{project_id}'/ 'commits'

    for dir in [commit_list_dir, commit_coverage_dir]:
        os.makedirs(dir, exist_ok=True)

    (commit_response, _) = commit_route.get(project_id)
    
    store(commit_list_dir, f'commits.json', commit_response)

    for commit in tqdm(commit_response.get('commits', [])):
        commit_id = commit.get('id')

        (coverage_response, status) = coverage.get(project_id, commit_id)        
        if status != 200:
            continue

        store(commit_coverage_dir, f'{commit_id}.json',coverage_response)


@timeit
def get_method_coverage(project_id: int, base_dir: Path):
    methods_route = MethodsInProjectRoute()
    coverage = ProdMethodHistoryRoute()

    method_list_dir = base_dir / 'projects' / f'{project_id}'
    method_coverage_dir = base_dir / 'coverage' / f'{project_id}' / 'methods'

    for dir in [method_list_dir, method_coverage_dir]:
        os.makedirs(dir, exist_ok=True)

    (method_response, _) = methods_route.get(project_id)
    
    store(method_list_dir, f'methods.json', method_response)

    for method in tqdm(method_response.get('methods', [])):
        method_id = method.get('id')

        (coverage_response, status) = coverage.get(project_id, method_id)        
        if status != 200:
            continue

        store(method_coverage_dir, f'{method_id}.json', coverage_response)


@timeit
def get_test_coverage(project_id: int, base_dir: Path):
    logger.info("Start obtaining test coverage")
    tests_route = TestMethodsInCommitRoute()
    coverage = TestMethodHistoryRoute()

    test_list_dir = base_dir / 'projects' / f'{project_id}'
    test_coverage_dir = base_dir / 'coverage' / f'{project_id}' / 'tests'

    for dir in [test_list_dir, test_coverage_dir]:
        os.makedirs(dir, exist_ok=True)

    logger.info("Get all tests")
    (test_response, _) = tests_route.get(project_id)

    store(test_list_dir, f'tests.json', test_response)

    logger.info("Obtain test coverage...")
    for test in tqdm(test_response.get('tests', [])):
        test_id = test.get('id')

        (coverage_response, status) = coverage.get(project_id, test_id)        
        if status != 200:
            continue

        store(test_coverage_dir, f'{test_id}.json', coverage_response)


def store(directory: Path, object_id, content):
    file_path = directory
    file_path = file_path / object_id

    with open(file_path, 'w+') as f:
        json.dump(content, f)


def execute_task(task):
    (func, project_id, base_dir) = task
    func(project_id, base_dir)


def extract_coverage(database: Path, output_path: Path):

    Config.DATABASE_PATH = database.resolve()

    (engine, Session) = create_engine_and_session()
    init_db(engine)

    project_route = ProjectsRoute()

    (projects_response, _) = project_route.get()

    root_dir = Path(output_path)

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    store(root_dir, 'projects.json', projects_response)

    collectors = [get_commit_coverage, get_method_coverage, get_test_coverage]
    projects: List[Dict] = projects_response.get('projects', [])

    logger.info(projects)

    # A task is a tuple of Projects collectors needed to be run
    tasks = []
    for project in projects:
        for collector in collectors:
            tasks.append((collector, project.get('id'), root_dir))

    # Exectute all the tasks one by one using all cpus:
    with Pool() as p:
        p.map(execute_task, tasks)
