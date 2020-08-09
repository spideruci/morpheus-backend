from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler
from pprint import pprint

def test_adding_project_to_table():
    # Given a project and a database in memory
    projects = ["spidertools",  "blinky", "tacoco"]
    project_db_handler = ProjectTableHandler(":memory:")

    # When: the project is added to the database
    for idx, project in enumerate(projects):
        project_id = project_db_handler.add_project(project)
        assert project_id == idx + 1
 
    # Then: it should be in the database
    for project in projects: 
        assert project_db_handler.get_project_id(project) is not None


def test_adding_commits_to_table():
    # Given a project, three commits sha, and a database in memory
    project = "spidertools"
    commits = [
        '1cb7348d6e164bac5538221998fceaf8a4c8df6a',
        '0ed92c9fa09a13a5b033b3943ebe9b737a6394e5',
        'a84873b9932e395dc0f0dcf59a9eb478208869f0'
    ]
    project_db_handler = ProjectTableHandler(":memory:")
    commit_db_handler = CommitTableHandler(":memory:")

    # When: the project and commits are added to the database
    project_id = project_db_handler.add_project(project)

    for idx, commit in enumerate(commits):
        commit_id = commit_db_handler.add_commit(project_id, commit)
        assert commit_id == idx + 1

    # Then: it should be in the database
    for i, commit in enumerate(commits):
        assert commit_db_handler.get_commit_id(project_id, commit) is not None

def test_adding_coverage_to_table():
    # Given: some coverage of a specific project and commit, and placed in a database
    db_path = ':memory:'
    project_db_handler = ProjectTableHandler(db_path)
    commit_db_handler = CommitTableHandler(db_path)
    coverage_handler = MethodCoverageHandler(db_path)
    
    project_id = project_db_handler.add_project("test")
    commit_id = commit_db_handler.add_commit(project_id, '1cb7348d6e164bac5538221998fceaf8a4c8df6a')

    prod_methods = [
        {
            "methodName": "write",
            "className": "IOUtils",
            "packageName": "org.apache.commons.io",
            "test_ids": [0]
        },
        {
            "methodName": "toString",
            "className": "DelegateFileFilter",
            "packageName": "org.apache.commons.io.filefilter",
            "test_ids": [0, 1]
        }
    ]

    test_methods = [
        {
            "test_id": 0,
            "test_name": "testFileCleanerDirectory.[engine:junit-vintage]/[runner:org.apache.commons.io.FileCleaningTrackerTestCase]/[test:testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)]",
            "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
            "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)"
        },
        {
            "test_id": 1,
            "test_name": "testFileCleanerDirectory_ForceStrategy.[engine:junit-vintage]/[runner:org.apache.commons.io.FileCleaningTrackerTestCase]/[test:testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)]",
            "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
            "method_name": "testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)"
        }
    ]

    coverage_handler.add_project_coverage(project_id, commit_id, prod_methods, test_methods)

    # When: requesting the data
    result = coverage_handler.get_project_coverage(commit_id)
    assert len(result["links"]) == 3
    assert len(result["methods"]) == 2
    assert len(result["tests"]) == 2