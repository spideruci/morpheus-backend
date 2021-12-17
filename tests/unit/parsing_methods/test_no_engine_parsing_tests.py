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

    def test_parsing_commons_io_parameterized_test(self):
        test_string = "testDataIntegrityWithBufferedReader[8](org.apache.commons.io.input.ReversedLinesFileReaderTestParamFile)"

        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.input"
        assert class_name == "ReversedLinesFileReaderTestParamFile"
        assert method_name == "testDataIntegrityWithBufferedReader[8]"
        assert is_passing