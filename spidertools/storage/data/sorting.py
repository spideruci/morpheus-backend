from typing import List, Dict
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from scipy.sparse import dok_matrix
import numpy as np
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


def cluster_tests(coverage: Dict, threshold=0.3) -> Dict:

    tests = coverage["tests"]
    methods = coverage["methods"]
    links = coverage["links"]

    test_id_map = dict()
    for i, test in enumerate(tests):
        if 'test_id' in test:
            test_id_map[test['test_id']] = i
        else:
            print(test)
    
    method_id_map = dict()
    for i, method in enumerate(methods):
        if 'method_id' in method:
            method_id_map[method['method_id']] = i
        else:
            print(method)

    sparse = dok_matrix((len(methods) + 1, len(tests) + 1), dtype=np.int)
    sparse.transpose()
    for link in links:
        try:
            sparse[method_id_map[link['method_id']], test_id_map[link['test_id']]] = 1
        except Exception as e:
            print(e)

    method_labels = AgglomerativeClustering(
        n_clusters=None,
        affinity='euclidean',
    ).fit_predict(sparse.todense())

    unique = np.unique(method_labels)

    return coverage
