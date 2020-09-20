def sort_by_name(coverage):
    prod_methods = coverage["methods"]
    test_methods = coverage["tests"]
    links = coverage["links"]

    prod_methods = sorted(prod_methods, key=lambda d: (d['package_name'],d['class_name'], d['method_name']))
    test_methods = sorted(test_methods, key=lambda d: (d['test_id'],))

    return {
        "methods": prod_methods,
        "tests": test_methods,
        "links": links
    }

