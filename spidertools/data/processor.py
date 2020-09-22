from typing import List, Callable

class ProcessDataBuilder():

    def __init__(self):
        self._filters = []
        self._sorter = None

    def add_filter(self, filter: Callable):
        self._filters.append(filter)
        return self

    def add_filters(self, filters : List[Callable]):
        self._filters.extend(filters)
        return self

    def set_sorter(self, sorter):
        self._sorter = sorter
        return self
    
    def process_data(self, data):
        result = data
        for f in self._filters:
            result = filter(f, result)

        if self._sorter is not None:
            result = self._sorter(result)
        
        return result
