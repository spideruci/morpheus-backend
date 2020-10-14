from spidertools.storage.models.methods import ProdMethod, ProdMethodVersion
from spidertools.storage.models.repository import Commit
from typing import Dict, List, Tuple


class MethodParser():
    def set_commit(self, commit: Commit):
        self.commit = commit
        return self

    def __parse_single_method(self, method_dict : Dict) -> ProdMethod:
        versions = method_dict['versions'][-1]

        prod_method = ProdMethod(
            method_name=method_dict['methodName'],
            method_decl=method_dict['methodDecl'],
            class_name=method_dict['className'],
            package_name=method_dict['packageName'],
            file_path=method_dict['filePath']
        )

        version = ProdMethodVersion(
            line_start=int(versions['lineStart']),
            line_end=int(versions['lineEnd']),
            commit=self.commit
        )

        return prod_method, version

    def parse(self, methods_dict: List[Dict]) -> List[ProdMethod]:
        test_filter = lambda m: not "test" in m["filePath"]
        methods_dict = list(filter(test_filter, methods_dict))
        return list(map(lambda method_dict : self.__parse_single_method(method_dict), methods_dict))

    def store(self, db_helper, project, commit, methods: List[ProdMethod]):
        with db_helper.create_session() as session:
            session.add(project)

            project.commits.append(commit)
            session.add(commit)

            for method, version in methods:
                method.project = project
                method, _ = session.add(method)

                version.method = method
                session.add(version)

        