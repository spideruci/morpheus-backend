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
        self.history = history
        self.properties = properties if properties is not None else {}

    def set_property(self, key, value):
        self.properties.update({key: value})

    def __hash__(self):
        return hash((self.methodDecl, self.className, self.packageName, self.filePath, self.lineStart, self.lineEnd))
    
    def __str__(self):
        return f"<Method: {self.methodDecl}, {self.className}, {self.packageName}, now:{self.lineStart}-{self.lineEnd}>"

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