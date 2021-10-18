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
import os

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
def get_commit_coverage(directory: Path, project_id):
    commit_route = CommitsRoute()
    coverage = MethodTestCoverageRoute()

    (commit_response, _) = commit_route.get(project_id)
    
    for commit in commit_response.get('commits'):
        commit_id = commit.get('id')

        (coverage_response, status) = coverage.get(project_id, commit_id)        
        if status != 200:
            print(f"[ERROR] {coverage_response} {status}")

        store(directory, f'{commit_id}.json',coverage_response)

@timeit
def get_method_coverage(directory: Path, project_id):
    methods_route = MethodsInProjectRoute()
    coverage = ProdMethodHistoryRoute()

    (method_response, _) = methods_route.get(project_id)
    
    for method in method_response.get('methods'):
        method_id = method.get('id')

        (coverage_response, status) = coverage.get(project_id, method_id)        
        if status != 200:
            print(f"[ERROR] {coverage_response} {status}")

        store(directory, f'{method_id}.json', coverage_response)

@timeit
def get_test_coverage(directory: Path, project_id):
    tests_route = TestMethodsInCommitRoute()
    coverage = TestMethodHistoryRoute()

    (test_response, _) = tests_route.get(project_id)
    
    for test in test_response.get('tests'):
        test_id = test.get('id')

        (coverage_response, status) = coverage.get(project_id, test_id)        
        if status != 200:
            print(f"[ERROR] {coverage_response} {status}")

        store(directory, f'{test_id}.json', coverage_response)

def store(directory: Path, object_id, content):
    file_path = directory
    file_path = file_path / object_id

    with open(file_path, 'w+') as f:
        json.dump(content, f)

def main():
    init_db(engine)

    project_route = ProjectsRoute()

    (projects_response, _) = project_route.get()

    root_dir = Path('/Users/kajdreef/code/2020/spidertools/test_output_dir')
    commit_dir = root_dir / 'commits'
    methods_dir = root_dir / 'methods'
    tests_dir = root_dir / 'tests'

    for dir in [root_dir, commit_dir, methods_dir, tests_dir]:
        if not os.path.exists(dir):
            os.mkdir(dir)

    for project in projects_response.get('projects'):
        project_id = project.get('id')
        get_commit_coverage(commit_dir, project_id)
        get_method_coverage(methods_dir, project_id)
        get_test_coverage(tests_dir, project_id)

if __name__ == '__main__':
    main()