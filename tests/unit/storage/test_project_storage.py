import unittest
from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler

class ProjectStorageTest(unittest.TestCase):
    def setUp(self):
        db_path = ':memory:'
        self.project_db_handler = ProjectTableHandler(db_path)

    def tearDown(self):
        # Close Databases:
        self.project_db_handler.close()

    def test_adding_project_to_table(self):
        # Given a project and a database in memory
        projects = ["spidertools",  "blinky", "tacoco"]

        # When: the project is added to the database
        for idx, project in enumerate(projects):
            project_id = self.project_db_handler.add_project(project)
            assert project_id == idx + 1
    
        # Then: it should be in the database
        for project in projects: 
            assert self.project_db_handler.get_project_id(project) is not None
