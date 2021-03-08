from morpheus.database.models.methods import ProdMethod, ProdMethodVersion
from morpheus.database.models.repository import Commit
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

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
            commit_id=self.commit.id
        )

        return prod_method, version

    def parse(self, methods_dict: List[Dict]) -> List[ProdMethod]:
        test_filter = lambda m: not "test" in m["filePath"]
        methods_dict = list(filter(test_filter, methods_dict))
        return list(map(lambda method_dict : self.__parse_single_method(method_dict), methods_dict))

    def store(self, session, project, commit, methods: List[ProdMethod]):
        method_count = session.query(ProdMethod).count()
        logger.info('Number of methods stored in DB: %s', method_count)

        for method, _ in methods:
            method.project_id = project.id

            if (session.query(ProdMethod) \
                .filter(
                    ProdMethod.project_id==method.project_id,
                    ProdMethod.method_name==method.method_name,
                    ProdMethod.method_decl==method.method_decl,
                    ProdMethod.class_name==method.class_name,
                    ProdMethod.package_name==method.package_name
                ).scalar()) is None:
                session.add(method)

        session.commit()

        for method, version in methods:
            if session.query(ProdMethodVersion)\
                .filter(
                    ProdMethodVersion.method_id==version.method_id,
                    ProdMethodVersion.commit_id==version.commit_id,
                    ProdMethodVersion.line_start==version.line_start,
                    ProdMethodVersion.line_end==version.line_end,
                ).scalar() is None:
                version.method_id = method.id
                session.add(version)

        session.commit()

        