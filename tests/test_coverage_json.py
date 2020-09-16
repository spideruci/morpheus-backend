import os
from spidertools.process_data.coverage_json import coverage_json
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler

def test_creating_method_coverage_file_jsoup():
    # Given:
    DB_PATH = ':memory:'
    project_handler = ProjectTableHandler(DB_PATH)
    commit_handler = CommitTableHandler(DB_PATH)
    coverage_handler = MethodCoverageHandler(DB_PATH)

    resource_dir = f'.{os.path.sep}tests{os.path.sep}resources{os.path.sep}'
    
    project_name = "jsoup"
    commit_sha = "2a2e8421c2aca89a21c786aa85af215dcbde02d7"
    coverage_matrix = f'{resource_dir}{project_name}{os.path.sep}{commit_sha}-cov-matrix.json'
    methods = f'{resource_dir}{project_name}{os.path.sep}methods-{commit_sha}.json'

    # When:
    output = coverage_json(methods, coverage_matrix, commit_sha)

    project_id = project_handler.add_project(project_name)
    commit_id = commit_handler.add_commit(project_id, commit_sha)
    coverage_handler.add_project_coverage(project_id, commit_id, output["methods"]["production"], output["methods"]["test"])

    # Then:
    output = coverage_handler.get_project_coverage(commit_id)
    assert output["links"] is not None
    assert len(output["links"]) != 0

def test_creating_method_coverage_file_commons_io():
    # Given:
    DB_PATH = ':memory:'
    project_handler = ProjectTableHandler(DB_PATH)
    commit_handler = CommitTableHandler(DB_PATH)
    coverage_handler = MethodCoverageHandler(DB_PATH)

    resource_dir = f'.{os.path.sep}tests{os.path.sep}resources{os.path.sep}'

    project_name = "commons-io"
    commit_sha = "6efbccc88318d15c0f5fdcfa0b87e3dc980dca22"
    coverage_matrix = f'{resource_dir}{project_name}{os.path.sep}{commit_sha}-cov-matrix.json'
    methods = f'{resource_dir}{project_name}{os.path.sep}methods-{commit_sha}.json'

    # When:
    output = coverage_json(methods, coverage_matrix, commit_sha)

    project_id = project_handler.add_project(project_name)
    commit_id = commit_handler.add_commit(project_id, commit_sha)
    coverage_handler.add_project_coverage(project_id, commit_id, output["methods"]["production"], output["methods"]["test"])

    # Then:
    output = coverage_handler.get_project_coverage(commit_id)
    assert output["links"] is not None
    assert len(output["links"]) != 0