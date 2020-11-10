from typing import List, Dict
from sklearn.cluster import AgglomerativeClustering
from treelib import Node, Tree
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

def cluster(coverage: Dict, threshold=0.1):
    coverage = cluster_methods(coverage, threshold=threshold)
    coverage = cluster_tests(coverage, threshold=threshold)
    return coverage

def cluster_methods(coverage: Dict, threshold=0.2) -> Dict:
    methods = coverage["methods"]
    cluster_labels = __clustering(coverage, threshold, transpose=False)

    for method, cluster_id in zip(methods, cluster_labels):
        method["cluster_id"] = cluster_id.item()

    # coverage['methods'] = __multi_key_sort(methods, ['cluster_id', 'package_name', 'class_name', 'method_name'])

    return coverage

def cluster_tests(coverage: Dict, threshold=0.2) -> Dict:
    tests = coverage["tests"]
    cluster_labels = __clustering(coverage, threshold, transpose=True)
    
    for test, cluster_id in zip(tests, cluster_labels):
        test["cluster_id"] = cluster_id.item()

    # coverage['tests'] = __multi_key_sort(tests, ['cluster_id', 'class_name', 'method_name'])

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
            logger.error('test_id not found in %s', test)
    
    method_id_map = dict()
    for i, method in enumerate(methods):
        if 'method_id' in method:
            method_id_map[method['method_id']] = i
        else:
            logger.error('method_id not found in %s', method)

    sparse = dok_matrix((len(methods), len(tests)), dtype=np.int)

    for edge in edges:
        try:
            sparse[method_id_map[edge['method_id']], test_id_map[edge['test_id']]] = 1
        except Exception as e:
            test_id = edge['test_id']
            method_id = edge['method_id']
            print(f'[ERROR] edge not in map { test_id } { method_id }')

    if transpose:
        sparse = sparse.transpose()

    model = AgglomerativeClustering(
        n_clusters=None,
        affinity='euclidean',
        distance_threshold=0,
        linkage='ward'
    ).fit(sparse.todense())

    return __label(model)

def __label(model):
    tree = Tree()

    input_length = len(model.labels_)
    root_node = input_length + len(model.children_) - 1
    tree.create_node(root_node, root_node)

    size = model.children_.shape[0]

    for idx in range(size):
        # Determine parent node
        parent = input_length + size - idx -1
        children = model.children_[size - idx -1]

        # Create children node
        tree.create_node(children[0], children[0], parent=parent)
        tree.create_node(children[1], children[1], parent=parent)

    leaves = []
    for l in tree.expand_tree(mode=1, reverse=True):
        node = tree.get_node(l)
        if not node.is_leaf():
            continue
        leaves.append(node.identifier)

    return leaves

def __multi_key_sort(objects: List, keys: List[str], reverse=False):
    objects = sorted(
        objects,
        key=lambda x : tuple([x[key] for key in keys]),
        reverse=reverse
    )
    return objects