from typing import Tuple, List, Dict, Set
import logging
from sqlalchemy.sql.sqltypes import Boolean
from spidertools.storage.models.methods import TestMethod, ProdMethod, ProdMethodVersion
from spidertools.storage.db_helper import row2dict
from spidertools.utils.timer import timer

logger = logging.getLogger(__name__)

@timer
def coverage_format(methods: List[Tuple[ProdMethod, ProdMethodVersion]], tests: List[TestMethod], edges: List[Tuple[int, int, Boolean]]) -> Dict:
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

def _merge_methods(method: Tuple[ProdMethod, ProdMethodVersion]):
    m: ProdMethod
    v: ProdMethodVersion

    m, v = method

    return {
        "method_id": v.id,
        "method_name": m.method_name,
        "method_decl": m.method_decl,
        "class_name": m.class_name,
        "package_name": m.package_name
    }

def _edge_formatter(edge):
    return {
        "test_id": edge[0],
        "method_id": edge[1],
        "color": edge[2]
    }