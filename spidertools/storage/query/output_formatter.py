from typing import Tuple, List, Dict, Set

from sqlalchemy.sql.sqltypes import Boolean
from spidertools.storage.models.methods import TestMethod, ProdMethod
from spidertools.storage.db_helper import row2dict
from spidertools.utils.timer import timer

@timer
def coverage_format(methods: List[ProdMethod], tests: List[TestMethod], edges: List[Tuple[int, int, Boolean]]) -> Dict:
    # Format to be send to the users.
    return {
        "edges": edges,
        "methods": list(map(row2dict, methods)),
        "tests": list(map(row2dict, tests))
    }