from typing import Dict, List, Tuple
from datetime import datetime

class Method():
    def __init__(self, methodName: str, methodDecl: str, className: str, packageName: str, filePath: str, lineStart: int, lineEnd: int, history: List, properties=None):
        self.methodName = methodName
        self.methodDecl = methodDecl
        self.className = className
        self.packageName = packageName
        self.filePath = filePath
        self.lineStart = lineStart
        self.lineEnd = lineEnd
        self.properties = properties if properties is not None else {}

    def set_property(self, key, value):
        self.properties.update({key: value})

    def __hash__(self):
        return hash((self.methodDecl, self.className, self.packageName, self.filePath, self.lineStart, self.lineEnd))
    
    def __str__(self):
        return f"<Method: {self.methodDecl}, {self.className}, {self.packageName}, now:{self.lineStart}-{self.lineEnd}>"

class ProdMethod():
    def __init__(self, method_name, method_decl, class_name, package_name, test_ids):
        self.method_name = method_name
        self.method_decl = method_decl
        self.class_name = class_name
        self.package_name = package_name
        self.test_ids = test_ids

class TestMethod():
    def __init__(self, test_id, class_name, method_name, test_result):
        self.test_id = test_id
        self.class_name = class_name
        self.method_name = method_name
        self.test_result = test_result

class TestEdge():
    def __init__(self, method_id: int, test_id: int):
        self._test_id = test_id  # Source
        self._method_id = method_id  # Target

    def get_test_id(self):
        return self._test_id

    def get_method_id(self):
        return self._method_id

def __get_boundary_versions(versions: List[Dict]) -> Tuple[Dict]:
    date_sort = lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%MZ")
    versions.sort(key=date_sort)
    then, now = versions.remove(0), versions.pop()
    return then, now

def __get_version(versions: List[Dict], sha: str):
    try:
        return next((version for version in versions if 'commitId' in version and version["commitId"] == sha), versions[-1])
    except KeyError as e:
        print(versions)
        print(e)
        exit(1)
    except IndexError as e:
        print(e)
        return None

def create_method_history_pairs(methods : List[Dict], then_sha: str, now_sha: str) -> List[Tuple[Method, Method]]:
    def convert_dict_to_method(method):
        methodName = method["methodName"]
        methodDecl = method["methodDecl"]
        className= method["className"]
        packageName= method["packageName"]
        filePath= method["filePath"]
        history = method["history"]

        then = __get_version(method["versions"], then_sha)
        now = __get_version(method["versions"], now_sha)

        now_method = Method(methodName, methodDecl, className, packageName, filePath, now["lineStart"], now["lineEnd"], history, now["properties"])
        then_method = Method(methodName, methodDecl, className, packageName, filePath, then["lineStart"], then["lineEnd"], history, then["properties"])

        return (now_method, then_method)
    
    # return zip(*list(map(convert_dict_to_method, methods)))
    return zip(*map(convert_dict_to_method, methods))
