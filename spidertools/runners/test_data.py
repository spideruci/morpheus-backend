import argparse
import os
import yaml
import json
from spidertools.utils.git_repo import GitRepo
from spidertools.tools.tacoco import TacocoRunner
from spidertools.tools.history import HistoryRunner, MethodParserRunner
from spidertools.process_data.coverage_json import coverage_json
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, BuildTableHandler, MethodCoverageTableHandler, TestMethodTableHandler, ProductionMethodTableHandler


if __name__ == "__main__":
    db_location = ":memory:"

    project_handler = ProjectTableHandler(db_location)
    commit_handler = CommitTableHandler(db_location)
    build_hanlder = BuildTableHandler(db_location)
    prod_hanlder = ProductionMethodTableHandler(db_location)
    test_hanlder = TestMethodTableHandler(db_location)

    file_path = "/Users/kajdreef/code/research/data/commons-cli/3f150ee61685fca466b38292144ce79d4755d749-combined.json"
    project = "commons-cli"
    commit_sha = "3f150ee61685fca466b38292144ce79d4755d749"

    project_handler.add_project(project)
    project_handler.get_project_id(project)
    commit_handler.add_commit(project_handler.get_project_id(project), commit_sha)
    
    build_hanlder.add_build_result(commit_handler.get_commit_id(project_handler.get_project_id(project), commit_sha), True)
    with open(file_path) as f:
        methods = json.load(f)["methods"]

    commit_id = commit_handler.get_commit_id(project_handler.get_project_id(project), commit_sha)
    for p in methods["production"]:
        method_hanlder.add_production_method(
            p["methodName"],
            p["className"],
            p["packageName"],
            commit_id
        )

    for p in methods["test"]:
        # TODO for some reason my data have it switched, so fix that.
        test_hanlder.add_test_method(
            p["test_name"],
            p["test_id"],
            commit_id
        )
    