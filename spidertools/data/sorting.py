from typing import List, Dict
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

def name(coverage):
    prod_methods: List[Dict] = coverage["methods"]
    test_methods: List[Dict]  = coverage["tests"]
    links: List[Dict] = coverage["links"]

    prod_methods = sorted(prod_methods, key=lambda d: (d['package_name'],d['class_name'], d['method_name']))
    test_methods = sorted(test_methods, key=lambda d: (d['test_id'],))

    return {
        "methods": prod_methods,
        "tests": test_methods,
        "links": links
    }

def cluster(coverage, threshold=0.1):
    model = AgglomerativeClustering(distance_threshold=threshold, linkage="average", compute_full_tree=True)
    model.fit_predict(list_of_methods)

    return {
        "methods": prod_methods,
        "tests": test_methods,
        "links": links
    }