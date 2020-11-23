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
    def get_method(self, method_id) -> List[ProdMethod]:
        return self._session.query(ProdMethod)\
            .filter(ProdMethod.project==self.project)\
            .filter(ProdMethod.id==method_id)\
            .first()

    @timer
    def get_methods(self) -> Tuple[ProdMethod, ProdMethodVersion]:
        return self._session.get_session().query(ProdMethod, ProdMethodVersion)\
            .join(ProdMethodVersion, (ProdMethodVersion.method_id==ProdMethod.id))\
            .filter(ProdMethod.project_id==self.project.id)\
            .filter(ProdMethodVersion.commit_id==self.commit.id)\
            .all()

    @timer
    def get_tests(self, method=None):
        return self._session.query(TestMethod)\
            .join(LineCoverage, (LineCoverage.test_id==TestMethod.id))\
            .filter(TestMethod.project_id==self.project.id)\
            .filter(LineCoverage.commit_id==self.commit.id)\
            .all()

    @timer
    def get_single_method_coverage(self, method) -> List[Tuple[Commit, List[Tuple[TestMethod, bool]]]]:

        # Obtain all method versions.
        method_versions: List[Tuple(ProdMethodVersion, Commit)] = self._session.get_session()\
            .query(ProdMethodVersion, Commit)\
            .join(ProdMethodVersion, ProdMethodVersion.commit_id==Commit.id)\
            .filter(ProdMethodVersion.method_id == method.id)\
            .all()

        result: List[Tuple[ProdMethodVersion, Commit, List[TestMethod]]] = list()

        # Get all Tests that cover a single method version id.
        for (version, commit) in method_versions:
            coverage = self._session.get_session()\
                .query(TestMethod, LineCoverage.test_id, LineCoverage.test_result) \
                .join(TestMethod, TestMethod.id==LineCoverage.test_id)\
                .filter(LineCoverage.method_version_id==version.id)\
                .group_by(TestMethod.id)\
                .all()

            tests = [(test, test_result) for test, _, test_result in coverage]
            result.append([commit, tests])

        return result

    @timer
    def get_coverage(self):
        return self._session.get_session()\
            .query(LineCoverage, ProdMethodVersion)\
            .join(ProdMethodVersion, (ProdMethodVersion.id==LineCoverage.method_version_id))\
            .filter(LineCoverage.commit_id==self.commit.id)\
            .group_by(LineCoverage.test_id, LineCoverage.method_version_id)\
            .all()
