import unittest
from spidertools.storage.table_handlers import ProductionMethodTableHandler
from spidertools.parsing_data.abstractions.method import ProdMethod
class ProjectStorageTest(unittest.TestCase):
    def setUp(self):
        db_path = ':memory:'
        self.prod_methods_db_handler = ProductionMethodTableHandler(db_path)

    def tearDown(self):
        # Close Databases:
        self.prod_methods_db_handler.close()

    def test_adding_production_methods_to_table(self):
        # Given a single test, try adding it two times to the database for different commits, should return the same test_id
        prod_method = ProdMethod(
            method_name="write",
            method_decl="void write()",
            class_name="IOUtils",
            package_name="org.apache.commons.io",
            test_ids=[0, 1]
        )

        # When: the project and commits are added to the database
        test_id1 = self.prod_methods_db_handler.add_production_method(0, 0, prod_method)
        test_id2 = self.prod_methods_db_handler.add_production_method(0, 1, prod_method)

        test_id3 = self.prod_methods_db_handler.add_production_method(1, 0, prod_method)
        test_id4 = self.prod_methods_db_handler.add_production_method(1, 1, prod_method)

        # Then: it should be in the database
        assert test_id1 == test_id2
        assert test_id3 == test_id4
        assert test_id1 != test_id3
        assert test_id1 != test_id4
