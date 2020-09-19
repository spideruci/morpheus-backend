import unittest
from spidertools.storage.table_handlers import ProductionMethodTableHandler

class ProjectStorageTest(unittest.TestCase):
    def setUp(self):
        print("SETUP")
        db_path = ':memory:'
        self.prod_methods_db_handler = ProductionMethodTableHandler(db_path)

    def tearDown(self):
        # Close Databases:
        self.prod_methods_db_handler.close()

    def test_adding_production_methods_to_table(self):
        # Given a single test, try adding it two times to the database for different commits, should return the same test_id
        prod_method = {
            "methodName": "toString",
            "methodDecl": "String toString()",
            "className": "DelegateFileFilter",
            "packageName": "org.apache.commons.io.filefilter",
            "test_ids": [0, 1]
        }        

        # When: the project and commits are added to the database
        test_id1 = self.prod_methods_db_handler.add_production_method(0, 0, prod_method['methodName'], prod_method['methodDecl'], prod_method['className'], prod_method['packageName'])
        test_id2 = self.prod_methods_db_handler.add_production_method(0, 1, prod_method['methodName'], prod_method['methodDecl'], prod_method['className'], prod_method['packageName'])

        test_id3 = self.prod_methods_db_handler.add_production_method(1, 0, prod_method['methodName'], prod_method['methodDecl'], prod_method['className'], prod_method['packageName'])
        test_id4 = self.prod_methods_db_handler.add_production_method(1, 1, prod_method['methodName'], prod_method['methodDecl'], prod_method['className'], prod_method['packageName'])

        # Then: it should be in the database
        assert test_id1 == test_id2
        assert test_id3 == test_id4
        assert test_id1 != test_id3
        assert test_id1 != test_id4
