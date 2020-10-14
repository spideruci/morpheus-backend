from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.models.methods import TestMethod, ProdMethod, ProdMethodVersion, LineCoverage
from sqlalchemy import func
from typing import List
from spidertools.utils.timer import timer


class ProjectQuery():
    def __init__(self, session):
        self._query = session.query(Project)

    @timer
    def get_projects(self) -> List[Project]:
        return self._query.all()

    @timer
    def get_project(self, project_name) -> Project:
        return self._query.filter(Project.project_name==project_name).first()
    

class CommitQuery():
    def __init__(self, session):
        self._query = session.query(Commit)

    @timer
    def get_commits(self, project_name) -> List[Commit]:
        return self._query\
            .filter(Project.project_name==project_name)\
            .all()

    @timer
    def get_commit(self, commit_sha) -> Commit:
        return self._query.filter(Commit.sha==commit_sha).first()


class MethodCoverageQuery():
    def __init__(self, session):
        self._session = session

    def set_commit(self, commit: Commit):
        self.commit: Commit= commit
        return self

    def set_project(self, project: Project):
        self.project: Project= project
        return self

    @timer
    def get_methods(self) -> List[ProdMethod]:
        return self._session.query(ProdMethod)\
            .join(ProdMethodVersion, (ProdMethodVersion.method_id==ProdMethod.id) & (ProdMethodVersion.commit==self.commit))\
            .filter(ProdMethod.project==self.project)\
            .all()

    @timer
    def get_tests(self):
        return self._session.query(TestMethod)\
            .join(LineCoverage, (LineCoverage.test_id==TestMethod.id) & (LineCoverage.commit==self.commit))\
            .filter(TestMethod.project==self.project)\
            .all()

    @timer
    def get_coverage(self):
        return self._session.get_session()\
            .query(LineCoverage.test_id, LineCoverage.method_version_id, LineCoverage.test_result)\
            .filter(LineCoverage.commit==self.commit)\
            .group_by(LineCoverage.test_id, LineCoverage.method_version_id)\
            .all()