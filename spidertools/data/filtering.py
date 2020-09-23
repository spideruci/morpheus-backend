import sys
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def no_filter(coverage: Dict):
    return coverage

# Test filters
def test_result(coverage: Dict, failed=False):
    # Filter based on if a test passed or failed
    logger.warn("Not implemented yet...")
    # Get all test we want to keep based on test result passed
    coverage["tests"] = list(filter(
        lambda x: bool(x['test_result']) == failed,
        coverage["tests"]
    ))

    test_ids = list(map(lambda x: x['test_id'], coverage["tests"]))

    # remove all links that contain those tests (test_id)
    coverage["links"] = list(filter(
        lambda x: x['test_id'] in test_ids,
        coverage["links"]
    ))

    # Update links and tests
    return coverage


def num_tests(coverage: Dict, threshold=10, compare_type=">"):
    # Filter based on number of tests < or > or ==
    # (Can be used to filter out methods that have no tests.) (no range)    
    if (compare_type == '='):
        compare_method = lambda x: x == threshold
    elif (compare_type == '>'):
        compare_method=lambda x: x > threshold
    else: # <
          compare_method=lambda x: x < threshold

    methods_ids = []
    method_id_count: Dict = {}
    for l in coverage["links"]:
        method_id = l['method_id']
        if method_id in method_id_count:
            method_id_count[method_id] += 1
        else:
            method_id_count[method_id] = 1
        
        if compare_method(method_id_count[method_id]):
            methods_ids.append(method_id)

    coverage["methods"] = list(filter(
        lambda x: x['method_id'] in methods_ids,
        coverage["methods"]
    ))
    coverage["links"] = list(filter(
        lambda x: x['method_id'] in methods_ids,
        coverage["links"]
    ))

    return coverage


def coverage(coverage: Dict, threshold=0, compare_type=">"):
    # Filter test methods based on the number of methods they cover.
       # Filter based on number of tests < or > or ==
    # (Can be used to filter out methods that have no tests.) (no range)
    logger.warn("Not implemented yet...")
    
    if (compare_type == '='):
        compare_method = lambda x: x == threshold
    elif (compare_type == '>'):
        compare_method=lambda x: x > threshold
    else: # <
          compare_method=lambda x: x < threshold

    test_ids = []
    test_id_count: Dict = {}
    for l in coverage["links"]:
        test_id = l['test_id']
        if test_id in test_id_count:
            test_id_count[test_id] += 1
        else:
            test_id_count[test_id] = 1
        
        if compare_method(test_id_count[test_id]):
            test_ids.append(test_id)

    coverage["tests"] = list(filter(
        lambda x: x['test_id'] in test_ids,
        coverage["tests"]
    ))
    coverage["links"] = list(filter(
        lambda x: x['test_id'] in test_ids,
        coverage["links"]
    ))
    return coverage


# Production filters
def cluster(coverage: Dict):
    # Filter out all production methods not belonging to a specific cluster
    logger.warn("Not implemented yet...")
    return coverage


def package(coverage: Dict):
    # Filter out all production methods not part of the specified package
    logger.warn("Not implemented yet...")
    return coverage


def cls(coverage: Dict):
    # Filter out all production methods not part of the specified class
    logger.warn("Not implemented yet...")
    return coverage

def method(coverage: Dict):
    # Filter to a specific production method
    logger.warn("Not implemented yet...")
    return coverage
