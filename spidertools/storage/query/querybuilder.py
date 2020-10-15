from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.models.methods import TestMethod, ProdMethod, ProdMethodVersion, LineCoverage
from typing import List, Tuple
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
    def get_commits(self, project: Project) -> List[Commit]:
        return self._query\
            .filter(Commit.project_id==project.id)\
            .all()

    @timer
    def get_commit(self, project: Project, commit_sha: str) -> Commit:
        return self._query\
            .filter(Commit.project_id==project.id)\
            .filter(Commit.sha==commit_sha)\
            .first()

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
    def get_method(self, method_name) -> List[ProdMethod]:
        return self._session.query(ProdMethod)\
            .filter(ProdMethod.project==self.project)\
            .filter(ProdMethod.method_name==method_name)\
            .first()

    @timer
    def get_methods(self) -> Tuple[ProdMethod, ProdMethodVersion]:
        return self._session.get_session().query(ProdMethod, ProdMethodVersion)\
            .join(ProdMethodVersion, (ProdMethodVersion.method_id==ProdMethod.id) & (ProdMethodVersion.commit_id==self.commit.id))\
            .filter(ProdMethod.project_id==self.project.id)\
            .all()

    @timer
    def get_tests(self, method=None):
        return self._session.query(TestMethod)\
            .join(LineCoverage, (LineCoverage.test_id==TestMethod.id) & (LineCoverage.commit_id==self.commit.id))\
            .filter(TestMethod.project_id==self.project.id)\
            .all()

    @timer
    def get_coverage(self):
        return self._session.get_session()\
            .query(LineCoverage.test_id, LineCoverage.method_version_id, LineCoverage.test_result)\
            .filter(LineCoverage.commit_id==self.commit.id)\
            .group_by(LineCoverage.test_id, LineCoverage.method_version_id)\
            .all()
