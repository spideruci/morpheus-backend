import unittest

from morpheus.analysis.parser.parsing_engines import parse_tacoco_test_string

class TestParsingTestMethodsNoEngine(unittest.TestCase):
    test_string = "testGetFreeSpaceWindows_String_EmptyMultiLineResponse(org.apache.commons.io.FileSystemUtilsTestCase)"

    def test_parsing_test_case(self):
        test_string = TestParsingTestMethodsNoEngine.test_string

        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io"
        assert class_name == "FileSystemUtilsTestCase"
        assert method_name == "testGetFreeSpaceWindows_String_EmptyMultiLineResponse"
        assert is_passing