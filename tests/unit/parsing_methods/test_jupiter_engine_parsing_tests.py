import unittest

from morpheus.analysis.parser.parsing_engines import TestEngine, determine_parsing_engine, parse_tacoco_test_string
class TestParsingJupiterTestMethods(unittest.TestCase):

    regular_test_string = "testMagicNumberFileFilterStringOffset().[engine:junit-jupiter]/[class:org.apache.commons.io.filefilter.FileFilterTestCase]/[method:testMagicNumberFileFilterStringOffset()]"

    def test_parsing_junit_jupiter_test_case_runtime(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.regular_test_string

        # Parse 
        engine = determine_parsing_engine(test_string)

        assert engine == TestEngine.JUPITER

    def test_parsing_junit_jupiter_test_case(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.regular_test_string

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.filefilter"
        assert class_name == "FileFilterTestCase"
        assert method_name == "testMagicNumberFileFilterStringOffset"
        assert is_passing

    parameterized_test_string = "[1] 0 files, 0 directories, 0 bytes.[engine:junit-jupiter]/[class:org.apache.commons.io.file.DeletingPathVisitorTest]/[test-template:testDeleteEmptyDirectory(org.apache.commons.io.file.DeletingPathVisitor)]/[test-template-invocation:#1]"

    def test_parsing_parameterized_test_case_runtime(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.parameterized_test_string

        # Parse 
        engine = determine_parsing_engine(test_string)

        assert engine == TestEngine.JUPITER

    def test_parsing_parameterized_test_case(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.parameterized_test_string

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.file"
        assert class_name == "DeletingPathVisitorTest"
        assert method_name == "testDeleteEmptyDirectory(org.apache.commons.io.file.DeletingPathVisitor)[1]"
        assert is_passing


    parameterized_test_string2 = "UnsynchronizedByteArrayOutputStream.toBufferedInputStream(InputStream, int).[engine:junit-jupiter]/[class:org.apache.commons.io.output.ByteArrayOutputStreamTestCase]/[test-template:testToBufferedInputStreamEmpty(java.lang.String, org.apache.commons.io.function.IOFunction)]/[test-template-invocation:#4]"

    def test_parsing_parameterized_test_case2(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.parameterized_test_string2

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.output"
        assert class_name == "ByteArrayOutputStreamTestCase"
        assert method_name == "testToBufferedInputStreamEmpty(java.lang.String, org.apache.commons.io.function.IOFunction)[4]"
        assert is_passing

    parameterized_test_string3 = "[1] ByteArrayOutputStream.[engine:junit-jupiter]/[class:org.apache.commons.io.output.ByteArrayOutputStreamTestCase]/[test-template:testToInputStreamEmpty(java.lang.String, org.apache.commons.io.output.ByteArrayOutputStreamTestCase$BAOSFactory)]/[test-template-invocation:#1]"

    def test_parsing_parameterized_test_case3(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.parameterized_test_string3

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.output"
        assert class_name == "ByteArrayOutputStreamTestCase"
        assert method_name == "testToInputStreamEmpty(java.lang.String, org.apache.commons.io.output.ByteArrayOutputStreamTestCase$BAOSFactory)[1]"
        assert is_passing

    parameterized_test_string4 = "test-file-utf8-win-linebr.bin, encoding\u003dUTF-8, blockSize\u003dnull, useNonDefaultFileSystem\u003dfalse, isResource\u003dtrue.[engine:junit-jupiter]/[class:org.apache.commons.io.input.ReversedLinesFileReaderTestParamFile]/[test-template:testDataIntegrityWithBufferedReader(java.lang.String, java.lang.String, java.lang.Integer, boolean, boolean)]/[test-template-invocation:#9]"

    def test_parsing_parameterized_test_case4(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.parameterized_test_string4

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.input"
        assert class_name == "ReversedLinesFileReaderTestParamFile"
        assert method_name == "testDataIntegrityWithBufferedReader(java.lang.String, java.lang.String, java.lang.Integer, boolean, boolean)[9]"
        assert is_passing


    def test_parsing_commons_lang_test_factory_testcase(self):
        test_string = "IllegalArgumentException.[engine:junit-jupiter]/[class:org.apache.commons.lang3.StreamsTest]/[test-factory:simpleStreamFilterFailing()]/[dynamic-test:#1]"

        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.lang3"
        assert class_name == "StreamsTest"
        assert method_name == "simpleStreamFilterFailing[1]"
        assert is_passing

    def test_parsing_commons_lang_nested_class_testcase(self):
        test_string = "shouldNotThrowExceptionWhenValueIsInstanceOfClass().[engine:junit-jupiter]/[class:org.apache.commons.lang3.ValidateTest]/[nested-class:IsInstanceOf]/[nested-class:WithMessageTemplate]/[method:shouldNotThrowExceptionWhenValueIsInstanceOfClass()]"

        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.lang3"
        assert class_name == "ValidateTest[IsInstanceOf[WithMessageTemplate]]"
        assert method_name == "shouldNotThrowExceptionWhenValueIsInstanceOfClass"
        assert is_passing
