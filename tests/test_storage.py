from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler

def test_adding_project_to_table():
    # Given a project and a database in memory
    db_path = ":memory:"
    projects = ["spidertools",  "blinky", "tacoco"]
    project_db_handler = ProjectTableHandler(db_path)

    # When: the project is added to the database
    for idx, project in enumerate(projects):
        project_id = project_db_handler.add_project(project)
        assert project_id == idx + 1
 
    # Then: it should be in the database
    for project in projects: 
        assert project_db_handler.get_project_id(project) is not None

def test_adding_commits_to_table():
    # Given a project, three commits sha, and a database in memory
    db_path = ':memory:'
    project = "spidertools"
    commits = [
        '1cb7348d6e164bac5538221998fceaf8a4c8df6a',
        '0ed92c9fa09a13a5b033b3943ebe9b737a6394e5',
        'a84873b9932e395dc0f0dcf59a9eb478208869f0'
    ]
    project_db_handler = ProjectTableHandler(db_path)
    commit_db_handler = CommitTableHandler(db_path)

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
            "methodDecl": "void write()",
            "className": "IOUtils",
            "packageName": "org.apache.commons.io",
            "test_ids": [0]
        },
        {
            "methodName": "toString",
            "methodDecl": "String toString()",
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
    assert len(result["methods"]) == 2
    assert len(result["tests"]) == 2
    assert len(result["links"]) == 3

def test_adding_same_production_method_for_different_commits():
    # Given: some coverage of a specific project and commit, and placed in a database
    db_path = ':memory:'
    project_db_handler = ProjectTableHandler(db_path)
    commit_db_handler = CommitTableHandler(db_path)
    coverage_handler = MethodCoverageHandler(db_path)

    project_id = project_db_handler.add_project("test")
    commit_id1 = commit_db_handler.add_commit(project_id, 'commit_1')
    commit_id2 = commit_db_handler.add_commit(project_id, 'commit_2')

    prod_methods = [{
        "methodName": "write",
        "methodDecl": "void write()",
        "className": "IOUtils",
        "packageName": "org.apache.commons.io",
        "test_ids": [0]
    }]

    # When: Adding the coverage information for both commits
    coverage_handler.add_project_coverage(project_id, commit_id1, prod_methods, [])
    coverage_handler.add_project_coverage(project_id, commit_id2, prod_methods, [])

    # Then: coverage should be the same
    coverage1 = coverage_handler.get_project_coverage(commit_id1)
    coverage2 = coverage_handler.get_project_coverage(commit_id2)

    assert coverage1 == coverage2

def test_adding_same_method_for_different_commits():
    # Given: some coverage of a specific project and commit, and placed in a database
    db_path = ':memory:'
    project_db_handler = ProjectTableHandler(db_path)
    commit_db_handler = CommitTableHandler(db_path)
    coverage_handler = MethodCoverageHandler(db_path)

    project_id = project_db_handler.add_project("test")
    commit_id1 = commit_db_handler.add_commit(project_id, 'commit_1')
    commit_id2 = commit_db_handler.add_commit(project_id, 'commit_2')

    prod_methods = [{
        "methodName": "write",
        "methodDecl": "void write()",
        "className": "IOUtils",
        "packageName": "org.apache.commons.io",
        "test_ids": [0]
    }]

    test_methods = [{
        "test_id": 0,
        "test_name": "testFileCleanerDirectory.[engine:junit-vintage]/[runner:org.apache.commons.io.FileCleaningTrackerTestCase]/[test:testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)]",
        "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
        "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)"
    }]

    # When: Adding the coverage information for both commits
    coverage_handler.add_project_coverage(project_id, commit_id1, prod_methods, test_methods)
    coverage_handler.add_project_coverage(project_id, commit_id2, prod_methods, test_methods)

    # Then: coverage should be the same
    coverage1 = coverage_handler.get_project_coverage(commit_id1)
    coverage2 = coverage_handler.get_project_coverage(commit_id2)

    assert len(coverage1['tests']) == 1
    assert len(coverage2['tests']) == 1
    assert coverage1 == coverage2


def test_adding_same_method_but_different_test_ids_for_different_commits():
    # Given: some coverage of a specific project and commit, and placed in a database
    db_path = ':memory:'
    project_db_handler = ProjectTableHandler(db_path)
    commit_db_handler = CommitTableHandler(db_path)
    coverage_handler = MethodCoverageHandler(db_path)

    project_id = project_db_handler.add_project("test")
    commit_id1 = commit_db_handler.add_commit(project_id, 'commit_1')
    commit_id2 = commit_db_handler.add_commit(project_id, 'commit_2')

    prod_methods_c1 = [
        {
            "methodName": "write",
            "methodDecl": "void write()",
            "className": "IOUtils",
            "packageName": "org.apache.commons.io",
            "test_ids": [0]
        },
        {
            "methodName": "toString",
            "methodDecl": "String toString()",
            "className": "DelegateFileFilter",
            "packageName": "org.apache.commons.io.filefilter",
            "test_ids": [0, 1]
        }
    ]

    test_methods_c1 = [
        {
            "test_id": 0,
            "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
            "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)"
        },
        {
            "test_id": 1,
            "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
            "method_name": "testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)"
        }
    ]

    prod_methods_c2 = [
        {
            "methodName": "write",
            "methodDecl": "void write()",
            "className": "IOUtils",
            "packageName": "org.apache.commons.io",
            "test_ids": [1]
        },
        {
            "methodName": "toString",
            "methodDecl": "String toString()",
            "className": "DelegateFileFilter",
            "packageName": "org.apache.commons.io.filefilter",
            "test_ids": [0, 1]
        }
    ]

    test_methods_c2 = [
        {
            "test_id": 0,
            "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
            "method_name": "testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)"
        },
        {
            "test_id": 1,
            "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
            "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)"
        }
    ]


    coverage_handler.add_project_coverage(project_id, commit_id1, prod_methods_c1, test_methods_c1)
    coverage_handler.add_project_coverage(project_id, commit_id2, prod_methods_c2, test_methods_c2)

    # When: requesting the data
    coverage_1 = coverage_handler.get_project_coverage(commit_id1)
    coverage_2 = coverage_handler.get_project_coverage(commit_id2)

    assert coverage_1 == coverage_2