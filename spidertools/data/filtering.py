import sys
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def no_filter(coverage: Dict):
    return coverage

# Test filters
def test_result(coverage: Dict, passed=False):
    # Filter based on if a test passed or failed
    logger.warn("Not implemented yet...")
    # Get all test we want to keep based on test result passed

    # remove all links that contain those tests (test_id)

    # Update links and tests
    return coverage


def num_tests(coverage: Dict):
    # Filter based on number of tests < or > or ==
    # (Can be used to filter out methods that have no tests.) (no range)
    logger.warn("Not implemented yet...")
    return coverage


def coverage(coverage: Dict):
    # Filter test methods based on the number of methods they cover.
    logger.warn("Not implemented yet...")
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
