from typing import Tuple, List, Dict, Set
import logging
from sqlalchemy.sql.sqltypes import Boolean
from spidertools.storage.models.methods import TestMethod, ProdMethod
from spidertools.storage.db_helper import row2dict
from spidertools.utils.timer import timer

logger = logging.getLogger(__name__)

@timer
def coverage_format(methods: List[ProdMethod], tests: List[TestMethod], edges: List[Tuple[int, int, Boolean]]) -> Dict:
    # Format to be send to the users.
    logger.debug("methods: %s, tests: %s, edges: %s", len(methods), len(tests), len(edges))

    return {
        "edges": list(map(_edge_formatter, edges)),
        "methods": list(map(row2dict, methods)),
        "tests": list(map(row2dict, tests))
    }

def _edge_formatter(edge):
    return {
        "method_id": edge[0],
        "test_id": edge[1],
        "pass": edge[2]
    }