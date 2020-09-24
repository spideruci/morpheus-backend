import os
import json
import numpy as np
import json
import re
from json import JSONEncoder
from numpy import savetxt
from typing import List, Dict
from spidertools.parsing_data.abstractions.method import Method, TestMethod, ProdMethod, create_method_history_pairs
from spidertools.parsing_data.metrics.coverage_metrics import LineCoverage, MethodCoverage

class MethodEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

def open_json_file(path: str):
    with open(path, 'r') as json_file:
        return json.load(json_file)
    return {}


def parse_test_method(test_method : str):
    # Parsing the class name
    if (result := re.search(r'runner:([a-zA-Z0-9._()$]+)', test_method)) is not None:
        class_name = result.group(1)
    elif (result := re.search(r'class:([a-zA-Z0-9._()$]+)', test_method)) is not None:
        class_name = result.group(1)
    elif (result := re.search(r'[a-zA-Z_0-9]+\(([a-zA-Z_0-9.$]+)\)', test_method)) is not None:
        class_name = result.group(1)
    else:
        print("[ERROR] class_name error: {}".format(test_method))
        class_name = ""

    # Parsing the method name aka test name.
    if (result := re.search(r'test:([a-zA-Z0-9._()$]+)', test_method)) is not None:
        method_name = result.group(1)
    elif (result := re.search(r'method:([a-zA-Z0-9._()$]+)', test_method)) is not None:
        method_name = result.group(1)
    elif (result := re.search(r'test-template:([a-zA-Z0-9._()$]+)', test_method)) is not None:
        method_name = result.group(1)
        invocation_number = re.search(r'test-template-invocation:#([0-9]+)', test_method).group(1)
        method_name = f'{method_name}/{invocation_number}'
    elif (result := re.search(r'([a-zA-Z_0-9]+)\([a-zA-Z_0-9.$]+\)', test_method)) is not None:
        method_name = result.group(1)
    else:
        print("[ERROR] test_name error: {}".format(test_method))
        method_name = ""

    # Parse if test passed or failed
    test_result = re.search(r'(_F$)', test_method) is not None

    return {
        "class_name": class_name,
        "method_name": method_name,
        "test_result": test_result
    }

def coverage_json(methods_path, coverage_path, commit_sha):
    methods: List[Dict] = open_json_file(methods_path)
    coverage = open_json_file(coverage_path)
    
    methods = list(filter(lambda m: not "test" in m["filePath"], methods))

    for m in methods:
        file_path = m["filePath"]
        if "src/main/java/" in file_path:
            file_path : str = file_path.split("src/main/java/")[-1]
        else:
            file_path : str = file_path.split("src/java/")[-1]
        
        m["filePath"] = file_path
    
    prod_methods = list(map(lambda m: Method(m['methodName'], m['methodDecl'], m['className'], m['packageName'], m['filePath'], m['versions'][-1]['lineStart'], m['versions'][-1]['lineEnd'], list()), methods))
    line_coverage = LineCoverage(coverage)
    method_coverage = MethodCoverage(line_coverage, prod_methods)

    test_methods = [ TestMethod(test_id=test_id, **parse_test_method(test)) for test_id, test in enumerate(coverage["testsIndex"])]

    # Create Method objects for all production methods and set the test_ids
    def convert_methods(method):
        test_ids = list(method_coverage.get_tests_testing(method))

        return ProdMethod(
            method.methodName,
            method.methodDecl,
            method.className,
            method.packageName,
            test_ids
        )

    prod_methods = list(map(
        convert_methods,
        prod_methods
    ))

    # Return the methods.
    return {
        "methods": {
            "production": prod_methods,
            "test": test_methods,
        }
    }
