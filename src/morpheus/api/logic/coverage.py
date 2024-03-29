import logging
from typing import Dict, List, Tuple
from morpheus.database.models.methods import LineCoverage, TestMethod, ProdMethod, ProdMethodVersion
from morpheus.database.models.repository import Project, Commit
from sqlalchemy import and_
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session

logger = logging.getLogger(__name__)


class CommitQuery():
    @staticmethod
    def get_commits(session, project: Project, ):
        return session.query(Commit)\
            .filter(Commit.project_id==project.id)\
            .order_by(Commit.id.desc())\
            .all()

    @staticmethod
    def get_commit(session, commit_id: int):
        return session.query(Commit)\
            .filter(Commit.id==commit_id)\
            .first()


class ProjectQuery():
    @staticmethod
    def get_projects(session):
        return session.query(Project)\
            .order_by(Project.project_name.desc()) \
            .all()

    @staticmethod
    def get_project(session, project_id: int):
        return session.query(Project)\
            .filter(Project.id==project_id)\
            .first()

class MethodQuery():
    @staticmethod
    def get_method(session, method_id):
        return session.query(ProdMethod)\
            .filter(ProdMethod.id==method_id)\
            .first()
    
    @staticmethod
    def exist(session, method_id):
        return session.query(ProdMethod.id) \
            .filter(ProdMethod.id==method_id) \
            .first()

    @staticmethod
    def get_method_versions(session: Session, method_id: int) -> List[ProdMethodVersion]:
        return session.query(ProdMethodVersion)\
            .filter(ProdMethodVersion.method_id==method_id)\
            .all()


class MethodCoverageQuery():
    @staticmethod
    def get_tests(session, project, commit)-> List[TestMethod]:
        return session.query(TestMethod) \
            .join(LineCoverage, (LineCoverage.test_id==TestMethod.id)) \
            .filter(and_(
                TestMethod.project_id==project.id,
                LineCoverage.commit_id==commit.id
            ))\
            .order_by(
                    TestMethod.package_name.desc(),
                    TestMethod.class_name.desc(),
                    TestMethod.method_name.desc()
            )\
            .all()

    @staticmethod
    def get_methods(session: Session, project: Project, commit: Commit=None)-> List[ProdMethod]:
        # This returns all the methods, but the edges point to method versions...
        query: Query = session.query(ProdMethod) \
            .join(ProdMethodVersion, (ProdMethodVersion.method_id==ProdMethod.id))\
            .filter(ProdMethod.project_id==project.id)
        
        if commit is not None:
            query = query.filter(ProdMethodVersion.commit_id==commit.id)

        return query.order_by(
                ProdMethod.package_name.desc(),
                ProdMethod.class_name.desc(),
                ProdMethod.method_decl.desc()
        ).all()

    @staticmethod
    def get_edges(session, commit: Commit) -> List[Dict]:
        result = session.query(LineCoverage.test_id, ProdMethodVersion.method_id, LineCoverage.test_result) \
            .join(ProdMethodVersion, (ProdMethodVersion.id==LineCoverage.method_version_id))\
            .filter(LineCoverage.commit_id==commit.id)\
            .group_by(LineCoverage.test_id, LineCoverage.method_version_id)\
            .all()
        
        edge_2_dict = lambda e: {'test_id': e[0], 'method_id': e[1], 'test_result': e[2]}

        return list(map(edge_2_dict, result))

class HistoryQuery():
    @staticmethod
    def get_method_history(session, method: ProdMethod) -> List[Tuple[TestMethod, LineCoverage]]:
        version: ProdMethodVersion
        result = []
        for version in method.versions:
            coverage = session.query(TestMethod, LineCoverage) \
                .join(LineCoverage, TestMethod.id == LineCoverage.test_id)\
                .filter(LineCoverage.method_version_id==version.id)\
                .all()

            result.append(coverage)

        return result

class MethodVersionQuery():

    @staticmethod
    def get_linked_tests(session, method_version: ProdMethodVersion):
        pass
