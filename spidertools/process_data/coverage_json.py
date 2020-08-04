import os
import json
import numpy as np
import json
import re
from json import JSONEncoder
from numpy import savetxt
from pprint import pprint
from typing import List, Dict
from spidertools.process_data.metrics.method import Method, create_method_history_pairs
from spidertools.process_data.metrics.coverage_metrics import LineCoverage, MethodCoverage, PerTestCaseCoverageMap

class MethodEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

def open_json_file(path: str):
    with open(path, 'r') as json_file:
        return json.load(json_file)
    return {}


def parse_test_method(test_method : str):
    try:
        class_name = re.search(r'runner:([a-zA-Z._()]+)', test_method).group(1)
        method_name = re.search(r'test:([a-zA-Z._]()+)', test_method).group(1)
    except:
        class_name = ""
        method_name = ""
        print("test_name error: {}".format(test_method))

    return {
        "test_name": test_method,
        "class_name": class_name,
        "method_name": method_name
    }

def coverage_json(methods_path, coverage_path, output_path, commit_sha):
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

    test_methods = [ {"test_id": test_id, **parse_test_method(test)} for test_id, test in enumerate(coverage["testsIndex"])]

    # Now create map between all production and which tests test it.
    matrix = np.zeros((len(prod_methods), len(test_methods)))
    header = [f"{p.className}.{p.className}.{p.methodName}" for p in prod_methods]

    production_output : List[Dict] = []
    for method_index, p_method in enumerate(prod_methods):
        production_output.append({
            "methodName": p_method.methodName,
            "className": p_method.className,
            "packageName": p_method.packageName,
            "test_ids": list(method_coverage.get_tests_testing(p_method)),
        })

    output = {
        "methods": {
            "production": production_output,
            "test": test_methods,
        }
    }

    with open(output_path, 'w') as json_file:
        json.dump(output, json_file, indent=4)
        json_file.flush()
