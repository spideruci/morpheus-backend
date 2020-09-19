import unittest
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler

class CommitStorageTest(unittest.TestCase):
    def setUp(self):
        db_path = ':memory:'
        self.project_db_handler = ProjectTableHandler(db_path)
        self.commit_db_handler = CommitTableHandler(db_path)

    def tearDown(self):
        # Close Databases:
        self.project_db_handler.close()
        self.commit_db_handler.close()

    def test_adding_commits_to_table(self):
        # Given a project, three commits sha, and a database in memory
        
        project = "spidertools"
        commits = [
            '1cb7348d6e164bac5538221998fceaf8a4c8df6a',
            '0ed92c9fa09a13a5b033b3943ebe9b737a6394e5',
            'a84873b9932e395dc0f0dcf59a9eb478208869f0'
        ]

        # When: the project and commits are added to the database
        project_id = self.project_db_handler.add_project(project)

        for idx, commit in enumerate(commits):
            commit_id = self.commit_db_handler.add_commit(project_id, commit)
            assert commit_id == idx + 1

        # Then: it should be in the database
        for i, commit in enumerate(commits):
            assert self.commit_db_handler.get_commit_id(project_id, commit) is not None

