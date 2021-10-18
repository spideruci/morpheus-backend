import re
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TestEngine(Enum):
    JUPITER   = 'junit-jupiter',
    VINTAGE   = 'junit-vintage',
    TESTNG    = 'testng'
    ERROR     = 'error'

def determine_parsing_engine(test_string: str) -> TestEngine:
    match_result = re.search(r'engine:([a-zA-Z]+-*[a-zA-Z]+)', test_string)

    if match_result is None:
        logger.error("unable to find engine: %s", test_string)
        return TestEngine.ERROR

    engine = match_result.group(1)
    match engine:
        case 'junit-jupiter':
            return TestEngine.JUPITER
        case 'junit-vintage':
            return TestEngine.VINTAGE
        case _:
            logger.error("Engine '%s' is currently not supported.", engine)
            return TestEngine.ERROR
        

def parse_tacoco_test_string(test_string: str):
    engine = determine_parsing_engine(test_string)

    (package_name, class_name) = __parse_package_name(engine, test_string)
    method_name = __parse_method_name(engine, test_string)
    is_passing = __is_passing_test(test_string)

    return package_name, class_name, method_name, is_passing

def __parse_package_name(engine, test_method):
    path = ''
    match engine:
        case TestEngine.JUPITER:
            path = re.search(r'class:([a-zA-Z0-9\._()$]+)', test_method).group(1)
            if path is None:
                path = re.search(r'runner:([a-zA-Z0-9\._()$]+)', test_method).group(1)
        case TestEngine.VINTAGE:
            path = re.search(r'runner:([a-zA-Z0-9\._()$]+)', test_method).group(1)
    
    split_path = path.split('.')
    class_name = split_path[-1]
    package_name = '.'.join(split_path[0:len(split_path)-1])
    return package_name, class_name

def __parse_method_name(engine, test_method):
    method_name = None

    match engine:
        case TestEngine.JUPITER:
            # Regular test
            if (result := re.search(r'method:([\w%=,\-\.,\s\\]+\([\w\s,.$]*\))', test_method)) is not None:
                return result.group(1)

            # Parameterized Tests
            elif (result := re.search(r'test-template:([\w%=,\-\.,\s\\]+\([\w\s\-,.$]*\))', test_method)) is not None:
                method_name = result.group(1)
                invocation_number = re.search(r'test-template-invocation:#([0-9]+)', test_method).group(1)
                return f'{method_name}[{invocation_number}]'

        case TestEngine.VINTAGE:
            # results = re.search(r'test:([\w%=,\-\.,\s\\]+\([\w\s,.$]*\))', test_method)
            results = re.findall(r'(test:)', test_method)
            match len(results):
                case 1:
                    result = re.search(r'test:([\w%=,\-\.,\s\\]+\([\w\s,.$]*\))', test_method)
                    return result.group(1)
                case 2:
                    result_p1 = re.search(r'test:([\w%=,\-\.,\s\\]+\([\w\s,.$]*\))', test_method).group(1)
                    result_p2 = re.search(r'test:([\w%=,\-\.,\s\\]+)', test_method).group(1)
                    return f"{result_p1}[{result_p2}]"
                case _:
                    return test_method.split('.')[0]

            # elif (result := re.findall(r'\[test:([^\]\[]+)\]', test_method)) is not None:
            #     if len(result) > 1:
                    
            #     else:
            #         return result[0]
    raise Exception("Unable to parse method")

def __is_passing_test(test_method):
    # Parse if test passed or failed
    return re.search(r'(_F$)', test_method) is None