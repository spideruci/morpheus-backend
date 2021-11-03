from argparse import ArgumentParser
import functools
import logging
from morpheus.api.endpoints.project_routes import ProjectsRoute, CommitsRoute
from morpheus.api.endpoints.methods_routes import MethodsInProjectRoute
from morpheus.api.endpoints.tests_routes import TestMethodsInCommitRoute
from morpheus.api.endpoints.coverage_routes import MethodTestCoverageRoute, ProdMethodHistoryRoute, TestMethodHistoryRoute
from morpheus.database.db import engine, init_db
from functools import wraps
from time import time
import json
from enum import Enum
from pathlib import Path
from morpheus.database.models.repository import Commit
from multiprocessing import Pool, cpu_count
import os

logger = logging.getLogger(__name__)

def init_logger(logging_level=logging.DEBUG):
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s] %(asctime)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        time_start = time()
        result = f(*args, **kw)
        time_end = time()
        diff = time_end - time_start
        print(f'func:{f.__name__}: {diff} sec')
        return result
    return wrap

@timeit
def get_commit_coverage(project_id: int, base_dir: Path):
    commit_route = CommitsRoute()
    coverage = MethodTestCoverageRoute()

    commit_list_dir = base_dir / 'projects' / f'{project_id}'
    commit_coverage_dir = base_dir / 'coverage'  / f'{project_id}'/ 'commits'

    for dir in [commit_list_dir, commit_coverage_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    (commit_response, _) = commit_route.get(project_id)
    
    store(commit_list_dir, f'commits.json', commit_response)

    for commit in commit_response.get('commits'):
        commit_id = commit.get('id')

        (coverage_response, status) = coverage.get(project_id, commit_id)        
        if status != 200:
            print(f"[ERROR] {coverage_response} {status}")

        store(commit_coverage_dir, f'{commit_id}.json',coverage_response)

@timeit
def get_method_coverage(project_id: int, base_dir: Path):
    methods_route = MethodsInProjectRoute()
    coverage = ProdMethodHistoryRoute()

    method_list_dir = base_dir / 'projects' / f'{project_id}'
    method_coverage_dir = base_dir / 'coverage' / f'{project_id}' / 'methods'

    for dir in [method_list_dir, method_coverage_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    (method_response, _) = methods_route.get(project_id)
    
    store(method_list_dir, f'methods.json', method_response)

    for method in method_response.get('methods'):
        method_id = method.get('id')

        (coverage_response, status) = coverage.get(project_id, method_id)        
        if status != 200:
            print(f"[ERROR] {coverage_response} {status}")

        store(method_coverage_dir, f'{method_id}.json', coverage_response)

@timeit
def get_test_coverage(project_id: int, base_dir: Path):
    tests_route = TestMethodsInCommitRoute()
    coverage = TestMethodHistoryRoute()

    test_list_dir = base_dir / 'projects' / f'{project_id}'
    test_coverage_dir = base_dir / 'coverage' / f'{project_id}' / 'tests'

    for dir in [test_list_dir, test_coverage_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    (test_response, _) = tests_route.get(project_id)

    store(test_list_dir, f'tests.json', test_response)

    for test in test_response.get('tests'):
        test_id = test.get('id')

        (coverage_response, status) = coverage.get(project_id, test_id)        
        if status != 200:
            print(f"[ERROR] {coverage_response} {status}")

        store(test_coverage_dir, f'{test_id}.json', coverage_response)


def store(directory: Path, object_id, content):
    file_path = directory
    file_path = file_path / object_id

    with open(file_path, 'w+') as f:
        json.dump(content, f)

def parse_arguments():
    parser = ArgumentParser(description='Create morpheus database')

    parser.add_argument('output', type=str, help='Output directory.')

    return parser.parse_args()


def main():
    init_logger()
    init_db(engine)

    args = parse_arguments()

    project_route = ProjectsRoute()

    (projects_response, _) = project_route.get()

    root_dir = Path(args.output)

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    store(root_dir, 'projects.json', projects_response)


    with Pool(cpu_count()) as p:
        collectors = [get_commit_coverage, get_method_coverage, get_test_coverage]
        projects = projects_response.get('projects')

        logger.info(projects)
        for f in collectors:
            project_ids = map(lambda p : p.get('id'), projects)
            p.map(functools.partial(f, base_dir=root_dir), project_ids)

if __name__ == '__main__':
    main()