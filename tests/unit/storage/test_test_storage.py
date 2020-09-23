from spidertools.storage.table_handlers import ProjectTableHandler, CommitTableHandler, MethodCoverageHandler, TestMethodTableHandler, ProductionMethodTableHandler
from spidertools.parsing_data.abstractions.method import TestMethod

def test_adding_tests_to_table():
    # Given a single test, try adding it two times to the database for different commits, should return the same test_id
    db_path = ':memory:'

    test_db_handler = TestMethodTableHandler(db_path)

    # When: the project and commits are added to the database
    test_method = TestMethod(
        test_id=0,
        class_name="org.apache.commons.io.FileCleaningTrackerTestCase",
        method_name="testFileCleanerDirectory(org.apache.commons.io.FileCleaningTrackerTestCase)",
        test_result=True
    )
    
    test_id1 = test_db_handler.add_test_method(0, 0, test_method)
    test_id2 = test_db_handler.add_test_method(0, 1, test_method)

    test_id3 = test_db_handler.add_test_method(1, 0, test_method)
    test_id4 = test_db_handler.add_test_method(1, 1, test_method)

    # Then: it should be in the database
    assert test_id1 == test_id2
    assert test_id3 == test_id4
    assert test_id1 != test_id3
    assert test_id1 != test_id4
