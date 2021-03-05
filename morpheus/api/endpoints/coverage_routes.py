from flask_restx.resource import Resource
from morpheus.api.rest import api
from morpheus.database.db import Session
from morpheus.database.util import row2dict
from morpheus.database.models.repository import Project, Commit
from morpheus.database.models.methods import LineCoverage, ProdMethod, ProdMethodVersion, TestMethod
from morpheus.api.logic.coverage import MethodCoverageQuery, CommitQuery, ProjectQuery, MethodQuery

ns = api.namespace(
    name='coverage',
    description='Endpoint to obtain different kind of coverage information for a given project, e.g., code coverage, or historical coverage.',
    authorization=False
)

############################################################### 
# Coverage routes
# - Methods v. Tests (given commit)
# - Tests v. Commits (given method)
# - Methods v. Commits (given tests)
###############################################################

@ns.route('/projects/<project_id>/commits/<commit_id>')
class MethodTestCoverageRoute(Resource):
    def get(self, project_id, commit_id):
        project: Project = ProjectQuery.get_project(Session, project_id)

        if project is None:
            return {"error": f"Commit with id '{project_id}' was not found..."}, 404

        commit: Commit = CommitQuery.get_commit(Session, commit_id)
        
        if commit is None:
            return {"error": f"Commit with id '{commit_id}' was not found..."}, 404

        methods = MethodCoverageQuery.get_methods(Session, project, commit)
        tests = MethodCoverageQuery.get_tests(Session, project, commit)
        edges = MethodCoverageQuery.get_edges(Session, commit)

        return {
            "project": row2dict(project),
            "commit": row2dict(commit),
            "coverage": {
                "methods": list(map(row2dict, methods)),
                "tests": list(map(row2dict, tests)),
                "edges": edges,
            }
        }, 200

@ns.route('/projects/<project_id>/methods/<method_id>')
class ProdMethodHistoryRoute(Resource):
    @ns.response(200, 'Success')
    @ns.response(404, 'Method not found.')
    def get(self, project_id, method_id):

        project: Project = ProjectQuery.get_project(Session, project_id)

        method : ProdMethod = MethodQuery.get_method(Session, method_id)

        if method is None:
            return {"msg": f'Method with id {method_id} not found...'}

        commits = []

        versions = Session.query(ProdMethodVersion)\
            .filter(ProdMethodVersion.method_id==method.id)\
            .all()

        for version in versions:
            commits.append(CommitQuery.get_commit(Session, version.commit_id))

        if not commits:
            return {'msg': 'fuck2'}

        versions_ids = [version.id for version in versions]
        edges = Session.query(LineCoverage.test_id, LineCoverage.commit_id, LineCoverage.test_result) \
            .filter(LineCoverage.method_version_id.in_(versions_ids)) \
            .group_by(LineCoverage.test_id, LineCoverage.method_version_id) \
            .all()

        edges_formatted = [{'test_id': test_id, 'commit_id': commit_id, 'test_result': test_result} for test_id, commit_id, test_result in edges]

        if not edges:
            return {'msg': 'Method is not covered by any test case.'}, 404
        
        test_ids = set(map(lambda edge: edge[0], edges))

        tests = Session.query(TestMethod) \
            .filter(TestMethod.project_id == project_id)\
            .filter(TestMethod.id.in_(test_ids)) \
            .all()

        return {
            "project": row2dict(project),
            "method": row2dict(method),
            "coverage": {
                "commits": list(map(row2dict, commits)),
                "tests": list(map(row2dict, tests)),
                "edges": edges_formatted
            }
        }, 200

@ns.route('/projects/<project_id>/tests/<test_id>')
class TestMethodHistoryRoute(Resource):
    @ns.response(200, 'Success')
    @ns.response(404, 'Test not found.')
    def get(self, project_id, test_id):

        project = Session.query(Project) \
            .filter(Project.id == project_id) \
            .first()

        if project is None:
            return {}, 404

        test: TestMethod = Session.query(TestMethod) \
            .filter(TestMethod.id == test_id) \
            .first()

        if test is None:
            return {"msg": 'Test was not found...'}, 404

        # Covered lines, but filtered to method and commit (so per pair only one covered line)
        edges = Session.query(LineCoverage.commit_id, LineCoverage.method_version_id, LineCoverage.test_result) \
            .filter(LineCoverage.test_id == test.id) \
            .group_by(LineCoverage.method_version_id, LineCoverage.commit_id) \
            .all()

        if edges is None or len(edges) == 0:
            return {"msg": "Test is not covering any methods."}, 404

        unique_method_version_id = set()
        unique_commit_ids = set()

        edges_formatted = list()
        for commit_id, method_version_id, result in edges:
            unique_method_version_id.add(method_version_id)
            unique_commit_ids.add(commit_id)
            edges_formatted.append({
                "commit_id": commit_id,
                "method_version_id": method_version_id,
                "test_result": result
            })


        methods = Session.query(ProdMethod, ProdMethodVersion.id) \
            .join(ProdMethodVersion, ProdMethod.id==ProdMethodVersion.method_id) \
            .filter(ProdMethodVersion.id.in_(unique_method_version_id)) \
            .group_by(ProdMethod, ProdMethodVersion.id) \
            .all()

        commits = Session.query(Commit) \
            .filter(
                Commit.project_id==project.id,
                Commit.id.in_(unique_commit_ids)
            ).all()
        
        def __merge_method_and_version(method_tuple):
            method, method_version_id = method_tuple
            method_dict = row2dict(method)
            method_dict['method_version_id'] = method_version_id
            return method_dict

        return {
            "project": row2dict(project),
            "test": row2dict(test),
            "coverage": {
                "commits": list(map(row2dict, commits)),
                "methods": list(map(__merge_method_and_version, methods)),
                "edges": edges_formatted,
            }
        }, 200