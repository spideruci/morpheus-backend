from inspect import getmembers, isfunction
import spidertools.data.filtering as filtering
import spidertools.data.sorting as sorting

def _selector(filter_type, module):
    # Get all filter functions
    results = getmembers(filtering, isfunction)

    # Return the actual function connected to the filter type.
    for t, f in results:
        if filter_type == t:
            return f

    return None

def filter_selector(filter_type):
    return _selector(filter_type, filtering)


def sort_selector(filter_type):
    return _selector(filter_type, sorting)
