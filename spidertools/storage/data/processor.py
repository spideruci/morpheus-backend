from typing import List, Callable, Dict

class ProcessDataBuilder():

    def __init__(self):
        self._filters: List[Callable] = []
        self._sorters: List[Callable] = []

    def add_filters(self, filters : List[Callable]):
        self._filters.extend(filters)
        return self

    def add_sorters(self, sorters: List[Callable]):
        self._sorters.extend(sorters)
        return self
    
    def process_data(self, data: Dict):
        result: Dict = data
        for f in self._filters:
            result: Dict = f(result)

        for sort in self._sorters:
            assert result is not None
            result: Dict = sort(result)
        
        return result
