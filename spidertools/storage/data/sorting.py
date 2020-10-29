from typing import List, Dict
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from scipy.sparse import dok_matrix
import numpy as np
import logging
from pprint import pprint

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

def cluster_methods(coverage: Dict, threshold=0.2) -> Dict:
    methods = coverage["methods"]
    cluster_labels = __clustering(coverage, threshold, transpose=False)

    for method, cluster_id in zip(methods, cluster_labels):
        method["cluster_id"] = cluster_id.item()

    coverage['methods'] = __multi_key_sort(methods, ['cluster_id', 'package_name', 'class_name', 'method_name'])

    return coverage

def cluster_tests(coverage: Dict, threshold=0.2) -> Dict:
    coverage = name(coverage)

    tests = coverage["tests"]
    cluster_labels = __clustering(coverage, threshold, transpose=True)
    
    for test, cluster_id in zip(tests, cluster_labels):
        test["cluster_id"] = cluster_id.item()

    coverage['tests'] = __multi_key_sort(tests, ['cluster_id', 'class_name', 'method_name'])

    return coverage

def __clustering(coverage: Dict, threshold, transpose=False) -> Dict:
    methods = coverage["methods"]
    tests = coverage["tests"]
    edges = coverage["edges"]

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

    sparse = dok_matrix((len(methods), len(tests)), dtype=np.int)
    if transpose:
        sparse = sparse.transpose()

    for edge in edges:
        try:
            sparse[method_id_map[edge['method_id']], test_id_map[edge['test_id']]] = 1
        except Exception as e:
            print(e)

    return AgglomerativeClustering(
        n_clusters=None,
        affinity='euclidean',
        distance_threshold=threshold,
    ).fit_predict(sparse.todense())

def __multi_key_sort(objects: List, keys: List[str], reverse=False):
    objects = sorted(
        objects,
        key=lambda x : tuple([x[key] for key in keys]),
        reverse=reverse
    )
    return objects