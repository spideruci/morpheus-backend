from typing import List, Dict
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
import logging

logger = logging.getLogger(__name__)


def name(coverage: Dict, reverse=False) -> Dict:
    logger.info("sort by name")
    return prod_name(test_name(coverage, reverse), reverse)


def prod_name(coverage: Dict, reverse=False) -> Dict:
    coverage["methods"] = sorted(
        coverage["methods"],
        key=lambda d: (d['package_name'], d['class_name'], d['method_name']),
        reverse=reverse
    )
    return coverage


def test_name(coverage: Dict, reverse=False) -> Dict:
    # Sort test Coverage data
    coverage["tests"] = sorted(
        coverage["tests"],
        key=lambda d: (d['class_name'], d['method_name']),
        reverse=reverse
    )
    return coverage


def cluster(coverage: Dict, threshold=0.1) -> Dict:
    logger.warn("Not implemented yet...")
    return coverage
