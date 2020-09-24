
from typing import Dict, List, Set, Optional
from spidertools.parsing_data.abstractions.method import Method
from datetime import date, datetime
from pprint import pprint

class LineCoverage():
    def __init__(self, coverage: Dict):
        self.line_coverage = self.__compute_coverage(coverage)

    def __compute_coverage(self, coverage) -> Dict:
        """
        Create a map between files and a map that contain as key: line number
        and value a list of test_id that covered that line in that file.
        """
        lines_covered = dict()

        # Iterate through the tacoco output and create a map for files and which lines are covered by which test
        for line_coverage in coverage['sources']:
            source = line_coverage['source']
            fullname = source['fullName']
            firstLine = int(source['firstLine'])
            lastLine = int(source['lastLine'])

            activating_tests = line_coverage['activatingTests']
            test_stmt_matrix = line_coverage['testStmtMatrix']

            # Check if there are any activating test cases for the current class
            if activating_tests is None:
                print(f"[Debug] this shouldn't happen:  {line_coverage}")
            elif len(activating_tests) == 0:
                print(f"[Info] '{fullname}' was not covered...")

            # Create a map between each line and which test case it is covered by.
            line_cov_dict: Dict[int, List[int]] = dict()
            for test_id, lines in zip(activating_tests, test_stmt_matrix):
                for i, line in enumerate(lines):
                    if line:
                        line_number = firstLine + i - 1
                        if line_number in line_cov_dict:
                            test_ids = line_cov_dict[line_number]
                            test_ids.append(test_id)
                            line_cov_dict[line_number] = test_ids
                        else:
                            line_cov_dict[line_number] = [test_id]
            
            lines_covered.update({fullname: line_cov_dict})

        return lines_covered

    def get_lines_covered(self, filename) -> List[int]:
        lines_covered = self.line_coverage.get(filename, None)
        if lines_covered:
            return list(lines_covered.keys())
        return []

    def get_test_cases_covering(self, filename: str, line: int):
        lines_covered = self.line_coverage.get(filename, None)
        if lines_covered is None:
            return []
        
        if line in lines_covered:
            return lines_covered.get(line)
        
        return []

    def is_line_covered(self, filename, line_number) -> bool:
        lines_covered_in_file : List[int] = self.get_lines_covered(filename)
        return line_number in lines_covered_in_file


class MethodCoverage():
    def __init__(self, line_coverage: LineCoverage, methods: List):
        self.__line_coverage = line_coverage
        self.method_coverage = self.__calculate_coverage(line_coverage, methods)

    def __calculate_coverage(self, line_coverage, methods):
        coverage = dict()
        
        for method in methods:
            file_name = method.filePath
            
            start_line = method.lineStart
            end_line = method.lineEnd

            lines_covered = line_coverage.get_lines_covered(file_name)
            if not lines_covered:
                coverage.update({method: 0})
                continue
            
            method_lines_covered = 0
            for i in range(start_line, end_line+1):
                if i in lines_covered:
                    method_lines_covered += 1

            percentage =  method_lines_covered / (end_line + 1 - start_line)

            coverage.update({method: percentage})
        
        return coverage

    def get_method_coverage(self, method) -> float:
        return self.method_coverage.get(method)
    
    def is_covered(self, method) -> bool:
        return self.get_method_coverage(method) > 0

    def get_tests_testing(self, method: Method):
        start : int = method.lineStart
        end : int = method.lineEnd

        test_ids = set()
        for i in range(start, end + 1):
            new_test_ids = self.__line_coverage.get_test_cases_covering(method.filePath, i)
            test_ids.update(new_test_ids)
        
        return test_ids

class PerTestCaseCoverageMap():
    def __init__(self, test_index: List[str], test_methods):
        self.__test_index = test_index
        self.test_change_map = self.__initialize_test_change_map(test_methods)

    def __initialize_test_change_map(self, test_methods: List[Method]) -> dict:

        test_index_date_map = {}
        for method in test_methods:
            methodName = method.methodName
            className = method.className
            packageName = method.packageName

            for index, test_name in enumerate(self.__test_index):
                # TODO Verify if this works for all different test name outputs tacoco generates...
                if (f"[class:{packageName}.{className}]" in test_name) and (f"[method:{methodName}(" in test_name):
                    test_index_date_map[index] = [ datetime.strptime(entry["date"], "%Y-%m-%dT%H:%MZ") for entry in method.history ]
                    break

        return test_index_date_map
    
    def get_test_index(self, test_method: Method) -> Optional[int]:
        methodName = test_method.methodName
        className = test_method.className
        packageName = test_method.packageName
        for index, test_name in enumerate(self.__test_index):
            # TODO Verify if this works for all different test name outputs tacoco generates...
            if (f"[class:{packageName}.{className}]" in test_name) and (f"[method:{methodName}(" in test_name):
                return index
        print (f"[class:{packageName}.{className}]", f"[method:{methodName}]")
        return None

    def get_test_changes_of_prod_method(self, method: Method) -> List[date]:
        test_changes = list()
        if "test_ids" in method.properties:
            for test_id in method.properties["test_ids"]:
                if test_id in self.test_change_map:
                    test_changes.extend(self.test_change_map[test_id])
        return test_changes

    def total_number_tests(self) -> int:
        return len(self.__test_index)

