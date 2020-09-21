import unittest
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler, ProductionMethodTableHandler


class StorageIntegrationTest(unittest.TestCase):

    def setUp(self):
        db_path = ':memory:'
        self.project_db_handler = ProjectTableHandler(db_path)
        self.commit_db_handler = CommitTableHandler(db_path)
        self.coverage_handler = MethodCoverageHandler(db_path)

    def tearDown(self):
        self.project_db_handler.close()
        self.commit_db_handler.close()
        self.coverage_handler.close()

    def test_adding_same_production_method_for_different_commits(self):
        # Given: some coverage of a specific project and commit, and placed in a database
        project_id = self.project_db_handler.add_project("test")
        commit_id1 = self.commit_db_handler.add_commit(project_id, 'commit_1')
        commit_id2 = self.commit_db_handler.add_commit(project_id, 'commit_2')

        prod_methods = [{
            "methodName": "write",
            "methodDecl": "void write()",
            "className": "IOUtils",
            "packageName": "org.apache.commons.io",
            "test_ids": [0]
        }]

        # When: Adding the coverage information for both commits
        self.coverage_handler.add_project_coverage(project_id, commit_id1, prod_methods, [])
        self.coverage_handler.add_project_coverage(project_id, commit_id2, prod_methods, [])

        # Then: coverage should be the same
        coverage1 = self.coverage_handler.get_project_coverage(commit_id1)
        coverage2 = self.coverage_handler.get_project_coverage(commit_id2)

        assert coverage1 == coverage2

    def test_adding_same_production_method_for_different_commits(self):
        # Given: some coverage of a specific project and commit, and placed in a database
        project_id = self.project_db_handler.add_project("test")
        commit_id1 = self.commit_db_handler.add_commit(project_id, 'commit_1')
        commit_id2 = self.commit_db_handler.add_commit(project_id, 'commit_2')

        prod_methods = [{
            "methodName": "write",
            "methodDecl": "void write()",
            "className": "IOUtils",
            "packageName": "org.apache.commons.io",
            "test_ids": [0]
        }]

        # When: Adding the coverage information for both commits
        self.coverage_handler.add_project_coverage(project_id, commit_id1, prod_methods, [])
        self.coverage_handler.add_project_coverage(project_id, commit_id2, prod_methods, [])

        # Then: coverage should be the same
        coverage1 = self.coverage_handler.get_project_coverage(commit_id1)
        coverage2 = self.coverage_handler.get_project_coverage(commit_id2)

        assert coverage1 == coverage2

    def test_adding_same_method_but_different_test_ids_for_different_commits(self):
        # Given: some coverage of a specific project and commit, and placed in a database
        project_id = self.project_db_handler.add_project("test")
        commit_id1 = self.commit_db_handler.add_commit(project_id, 'commit_1')
        commit_id2 = self.commit_db_handler.add_commit(project_id, 'commit_2')

        prod_methods1 = [
            {"test_ids": [0], "methodName": "write", "methodDecl": "void write()", "className": "IOUtils", "packageName": "org.apache.commons.io"},
            {"test_ids": [0, 1], "methodName": "toString", "methodDecl": "String toString()", "className": "DelegateFileFilter", "packageName": "org.apache.commons.io.filefilter"}
        ]

        prod_methods2 = [
            {"test_ids": [1], "methodName": "write", "methodDecl": "void write()", "className": "IOUtils", "packageName": "org.apache.commons.io"},
            {"test_ids": [1, 0], "methodName": "toString", "methodDecl": "String toString()", "className": "DelegateFileFilter", "packageName": "org.apache.commons.io.filefilter"}
        ]

        test_methods1 = [
            {"test_id": 1, "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase", "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)", "test_result": True},
            {"test_id": 0, "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase", "method_name": "testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)", "test_result": True}
        ]

        test_methods2 = [
            {"test_id": 0, "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase", "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)", "test_result": True},
            {"test_id": 1, "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase", "method_name": "testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)", "test_result": True}
        ]

        self.coverage_handler.add_project_coverage(project_id, commit_id1, prod_methods1, test_methods1)
        self.coverage_handler.add_project_coverage(project_id, commit_id2, prod_methods2, test_methods2)

        # When: requesting the data
        coverage_1 = self.coverage_handler.get_project_coverage(commit_id1)
        coverage_2 = self.coverage_handler.get_project_coverage(commit_id2)

        assert coverage_1 == coverage_2

    def test_adding_coverage_to_table(self):
        # Given: some coverage of a specific project and commit, and placed in a database
        project_id = self.project_db_handler.add_project("test")
        commit_id = self.commit_db_handler.add_commit(project_id, '1cb7348d6e164bac5538221998fceaf8a4c8df6a')

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
                "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
                "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)",
                "test_result": True
            },
            {
                "test_id": 1,
                "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
                "method_name": "testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)",
                "test_result": True
            }
        ]

        self.coverage_handler.add_project_coverage(project_id, commit_id, prod_methods, test_methods)

        # When: requesting the data
        result = self.coverage_handler.get_project_coverage(commit_id)
        assert len(result["methods"]) == 2
        assert len(result["tests"]) == 2
        assert len(result["links"]) == 3

    def test_adding_same_method_for_different_commits(self): 
        # Given: some coverage of a specific project and commit, and placed in a database
        project_id = self.project_db_handler.add_project("test")
        commit_id = self.commit_db_handler.add_commit(project_id, '1cb7348d6e164bac5538221998fceaf8a4c8df6a')

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
                "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
                "method_name": "testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)",
                "test_result": True
            },
            {
                "test_id": 1,
                "class_name": "org.apache.commons.io.FileCleaningTrackerTestCase",
                "method_name": "testFileCleanerDirectory_ForceStrategy(org.apache.commons.io.FileCleaningTrackerTestCase)",
                "test_result": True
            }
        ]

        self.coverage_handler.add_project_coverage(project_id, commit_id, prod_methods, test_methods)

        # When: requesting the data
        result = self.coverage_handler.get_project_coverage(commit_id)

        # THen:
        assert len(result["methods"]) == 2
        assert len(result["tests"]) == 2
        assert len(result["links"]) == 3
