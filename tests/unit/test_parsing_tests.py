import unittest

from morpheus.analysis.parser.parsing_engines import TestEngine, determine_parsing_engine, parse_tacoco_test_string

class TestParsingVintageTestMethods(unittest.TestCase):

    regular_test_string = "testHandleStartDirectoryFalse.[engine:junit-vintage]/[runner:org.apache.commons.io.DirectoryWalkerTestCaseJava4]/[test:testHandleStartDirectoryFalse(org.apache.commons.io.DirectoryWalkerTestCaseJava4)]"

    # parametirized_test_string = 

    def test_parsing_test_case_runtime(self):
        # Given a test case
        test_string = TestParsingVintageTestMethods.regular_test_string

        # Parse 
        engine = determine_parsing_engine(test_string)

        assert engine == TestEngine.VINTAGE

    def test_parsing_test_case(self):
        # Given a test case
        test_string = TestParsingVintageTestMethods.regular_test_string

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io"
        assert class_name == "DirectoryWalkerTestCaseJava4"
        assert method_name == "testHandleStartDirectoryFalse(org.apache.commons.io.DirectoryWalkerTestCaseJava4)"
        assert is_passing


class TestParsingJupiterTestMethods(unittest.TestCase):

    regular_test_string = "testMagicNumberFileFilterStringOffset().[engine:junit-jupiter]/[class:org.apache.commons.io.filefilter.FileFilterTestCase]/[method:testMagicNumberFileFilterStringOffset()]"

    def test_parsing_junit_vintage_test_case_runtime(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.regular_test_string

        # Parse 
        engine = determine_parsing_engine(test_string)

        assert engine == TestEngine.JUPITER

    def test_parsing_junit_vintage_test_case(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.regular_test_string

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.filefilter"
        assert class_name == "FileFilterTestCase"
        assert method_name == "testMagicNumberFileFilterStringOffset()"
        assert is_passing


    regular_test_string2 = "testUTF16LEFile[BlockSize\u003d4,096].[engine:junit-vintage]/[runner:org.apache.commons.io.input.ReversedLinesFileReaderTestParamBlockSize]/[test:%5BBlockSize\u003d4,096%5D]/[test:testUTF16LEFile%5BBlockSize\u003d4,096%5D(org.apache.commons.io.input.ReversedLinesFileReaderTestParamBlockSize)]"

    def test_parsing_test_case2(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.regular_test_string2

        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.input"
        assert class_name == "ReversedLinesFileReaderTestParamBlockSize"
        assert method_name == "testUTF16LEFile%5BBlockSize\u003d4,096%5D(org.apache.commons.io.input.ReversedLinesFileReaderTestParamBlockSize)[%5BBlockSize\u003d4,096%5D]"
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

    parameterized_test_string5 = "testDataIntegrityWithBufferedReader[test-file-utf8-win-linebr.bin, charset\u003dUTF-8].[engine:junit-vintage]/[runner:org.apache.commons.io.input.ReversedLinesFileReaderTestParamFile]/[test:%5Btest-file-utf8-win-linebr.bin, charset\u003dUTF-8%5D%5B0%5D]/[test:testDataIntegrityWithBufferedReader%5Btest-file-utf8-win-linebr.bin, charset\u003dUTF-8%5D(org.apache.commons.io.input.ReversedLinesFileReaderTestParamFile)]"

    def test_parsing_parameterized_test_case5(self):
        # Given a test case
        test_string = TestParsingJupiterTestMethods.parameterized_test_string5

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "org.apache.commons.io.input"
        assert class_name == "ReversedLinesFileReaderTestParamFile"
        assert method_name == "testDataIntegrityWithBufferedReader%5Btest-file-utf8-win-linebr.bin, charset\u003dUTF-8%5D(org.apache.commons.io.input.ReversedLinesFileReaderTestParamFile)[%5Btest-file-utf8-win-linebr.bin, charset\u003dUTF-8%5D%5B0%5D]"
        assert is_passing

class TestCucumberTest(unittest.TestCase):
    regular_test_string = "When the user presses the \"Start\" button.[engine:junit-vintage]/[runner:nl.tudelft.jpacman.e2e.framework.startup.StartupTest]/[test:rO0ABXNyAB9naGVya2luLmZvcm1hdHRlci5tb2RlbC5GZWF0dXJlAAAAAAAAAAECAAB4cgAkZ2hlcmtpbi5mb3JtYXR0ZXIubW9kZWwuVGFnU3RhdGVtZW50AAAAAAAAAAECAAJMAAJpZHQAEkxqYXZhL2xhbmcvU3RyaW5nO0wABHRhZ3N0ABBMamF2YS91dGlsL0xpc3Q7eHIAKmdoZXJraW4uZm9ybWF0dGVyLm1vZGVsLkRlc2NyaWJlZFN0YXRlbWVudInoQ7yJkLCFAgABTAALZGVzY3JpcHRpb25xAH4AAnhyACZnaGVya2luLmZvcm1hdHRlci5tb2RlbC5CYXNpY1N0YXRlbWVudPM3wIsDVBUvAgAETAAIY29tbWVudHNxAH4AA0wAB2tleXdvcmRxAH4AAkwABGxpbmV0ABNMamF2YS9sYW5nL0ludGVnZXI7TAAEbmFtZXEAfgACeHIAGmdoZXJraW4uZm9ybWF0dGVyLk1hcHBhYmxl42CLFPnowjUCAAB4cHNyABNqYXZhLnV0aWwuQXJyYXlMaXN0eIHSHZnHYZ0DAAFJAARzaXpleHAAAAAAdwQAAAAAeHQAB0ZlYXR1cmVzcgARamF2YS5sYW5nLkludGVnZXIS4qCk94GHOAIAAUkABXZhbHVleHIAEGphdmEubGFuZy5OdW1iZXKGrJUdC5TgiwIAAHhwAAAAAnQADVN0YXJ0IHRvIHBsYXl0AEBBcyBhIHBsYXllcgpJIHdhbnQgdG8gc3RhcnQgdGhlIGdhbWUKc28gdGhhdCBJIGNhbiBhY3R1YWxseSBwbGF5dAANc3RhcnQtdG8tcGxheXNxAH4ACQAAAAJ3BAAAAAJzcgAbZ2hlcmtpbi5mb3JtYXR0ZXIubW9kZWwuVGFnAAAAAAAAAAECAAJMAARsaW5lcQB%2BAAZMAARuYW1lcQB%2BAAJ4cQB%2BAAdzcQB%2BAAwAAAABdAADQFMxc3EAfgATcQB%2BABV0AApAZnJhbWV3b3JreA\u003d\u003d]/[test:rO0ABXNyACBnaGVya2luLmZvcm1hdHRlci5tb2RlbC5TY2VuYXJpbwAAAAAAAAABAgABTAAEdHlwZXQAEkxqYXZhL2xhbmcvU3RyaW5nO3hyACRnaGVya2luLmZvcm1hdHRlci5tb2RlbC5UYWdTdGF0ZW1lbnQAAAAAAAAAAQIAAkwAAmlkcQB%2BAAFMAAR0YWdzdAAQTGphdmEvdXRpbC9MaXN0O3hyACpnaGVya2luLmZvcm1hdHRlci5tb2RlbC5EZXNjcmliZWRTdGF0ZW1lbnSJ6EO8iZCwhQIAAUwAC2Rlc2NyaXB0aW9ucQB%2BAAF4cgAmZ2hlcmtpbi5mb3JtYXR0ZXIubW9kZWwuQmFzaWNTdGF0ZW1lbnTzN8CLA1QVLwIABEwACGNvbW1lbnRzcQB%2BAANMAAdrZXl3b3JkcQB%2BAAFMAARsaW5ldAATTGphdmEvbGFuZy9JbnRlZ2VyO0wABG5hbWVxAH4AAXhyABpnaGVya2luLmZvcm1hdHRlci5NYXBwYWJsZeNgixT56MI1AgAAeHBzcgATamF2YS51dGlsLkFycmF5TGlzdHiB0h2Zx2GdAwABSQAEc2l6ZXhwAAAAAHcEAAAAAHh0AAhTY2VuYXJpb3NyABFqYXZhLmxhbmcuSW50ZWdlchLioKT3gYc4AgABSQAFdmFsdWV4cgAQamF2YS5sYW5nLk51bWJlcoaslR0LlOCLAgAAeHAAAAAIdAASUHJlc3Mgc3RhcnQgYnV0dG9udAAAdAAgc3RhcnQtdG8tcGxheTtwcmVzcy1zdGFydC1idXR0b25zcQB%2BAAkAAAABdwQAAAABc3IAG2doZXJraW4uZm9ybWF0dGVyLm1vZGVsLlRhZwAAAAAAAAABAgACTAAEbGluZXEAfgAGTAAEbmFtZXEAfgABeHEAfgAHc3EAfgAMAAAAB3QABUBTMS4xeHQACHNjZW5hcmlv]/[test:rO0ABXNyABxnaGVya2luLmZvcm1hdHRlci5tb2RlbC5TdGVwAAAAAAAAAAECAAJMAApkb2Nfc3RyaW5ndAAjTGdoZXJraW4vZm9ybWF0dGVyL21vZGVsL0RvY1N0cmluZztMAARyb3dzdAAQTGphdmEvdXRpbC9MaXN0O3hyACZnaGVya2luLmZvcm1hdHRlci5tb2RlbC5CYXNpY1N0YXRlbWVudPM3wIsDVBUvAgAETAAIY29tbWVudHNxAH4AAkwAB2tleXdvcmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARsaW5ldAATTGphdmEvbGFuZy9JbnRlZ2VyO0wABG5hbWVxAH4ABHhyABpnaGVya2luLmZvcm1hdHRlci5NYXBwYWJsZeNgixT56MI1AgAAeHBzcgATamF2YS51dGlsLkFycmF5TGlzdHiB0h2Zx2GdAwABSQAEc2l6ZXhwAAAAAHcEAAAAAHh0AAVXaGVuIHNyABFqYXZhLmxhbmcuSW50ZWdlchLioKT3gYc4AgABSQAFdmFsdWV4cgAQamF2YS5sYW5nLk51bWJlcoaslR0LlOCLAgAAeHAAAAAKdAAjdGhlIHVzZXIgcHJlc3NlcyB0aGUgIlN0YXJ0IiBidXR0b25wcA\u003d\u003d]"


    def test_parsing_test_case_runtime(self):
        # Given a test case
        test_string = TestCucumberTest.regular_test_string

        # Parse 
        engine = determine_parsing_engine(test_string)

        assert engine == TestEngine.VINTAGE

    def test_parsing_test_case(self):
        # Given a test case
        test_string = TestCucumberTest.regular_test_string

        # Parse 
        package, class_name, method_name, is_passing = parse_tacoco_test_string(test_string)

        assert package == "nl.tudelft.jpacman.e2e.framework.startup"
        assert class_name == "StartupTest"
        assert method_name == "When the user presses the \"Start\" button"
        assert is_passing