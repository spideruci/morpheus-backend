from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from spidertools.process_data.metrics.method import Method
from typing import List

def cluster_methods(coverage, threshold=0.1):
    model = AgglomerativeClustering(distance_threshold=threshold, linkage="average", compute_full_tree=True)
    model.fit_predict(list_of_methods)

    return {
        "methods": prod_methods,
        "tests": test_methods,
        "links": links
    }