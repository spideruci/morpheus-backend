from typing import Tuple, List, Dict, Set
import logging
from sqlalchemy.sql.sqltypes import Boolean
from spidertools.storage.models.methods import TestMethod, ProdMethod, ProdMethodVersion, LineCoverage
from spidertools.storage.db_helper import row2dict
from spidertools.utils.timer import timer

logger = logging.getLogger(__name__)

@timer
def coverage_format(methods: List[Tuple[ProdMethod, ProdMethodVersion]], tests: List[TestMethod], edges: List[Tuple[LineCoverage, ProdMethodVersion]]) -> Dict:
    # Format to be send to the users.
    logger.debug("methods: %s, tests: %s, edges: %s", len(methods), len(tests), len(edges))
    return {
        "edges": list(map(_edge_formatter, edges)),
        "methods": list(map(_merge_methods, methods)),
        "tests": list(map(_test_format, tests))
    }

def _test_format(test: TestMethod):
    return {
        "class_name": test.class_name,
        "method_name": test.method_name,
        "test_id": test.id
    }

def _merge_methods(method: Tuple[ProdMethod, ProdMethodVersion]) -> Dict:
    m: ProdMethod
    v: ProdMethodVersion

    m, v = method

    return {
        "method_id": m.id,
        "method_version_id": v.id,
        "method_name": m.method_name,
        "method_decl": m.method_decl,
        "class_name": m.class_name,
        "package_name": m.package_name
    }

def _edge_formatter(edge: Tuple[LineCoverage, ProdMethodVersion]) -> Dict:
    line: LineCoverage
    version: ProdMethodVersion

    line, version = edge
    return {
        "test_id": line.test_id,
        "method_id": version.method_id,
        "method_version_id": version.id,
        "test_result": line.test_result
    }

@timer
def history_coverage_formatter(coverage: List[Tuple[LineCoverage, ProdMethodVersion, TestMethod]]) -> Dict:
    # Format to be send to the users.
    all_commits = set()
    commits = list()
    tests = []
    edges = []

    line: LineCoverage
    prodmethod: ProdMethodVersion
    test: TestMethod

    for line, prodmethod, test in coverage:
        # TODO make sure only unique commits are added
        if prodmethod.commit_id not in all_commits:
            commits.append( {"commit_id": prodmethod.commit_id})
            all_commits.add(prodmethod.commit_id)

        # TODO make sure only unique tests are added
        tests.append({
            "test_id": test.id,
            "class_name": test.class_name,
            "method_name": test.method_name
        })

        edges.append({
            "test_id": test.id,
            "commit_id": prodmethod.commit_id,
            "test_result": line.test_result
        })

    return {
        "commits": commits,
        "tests": tests,
        "edges": edges
    }