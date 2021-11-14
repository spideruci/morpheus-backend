from morpheus.database.models.methods import LineCoverage, ProdMethod, ProdMethodVersion, TestMethod
from flask_restx.resource import Resource
from morpheus.api.rest import api
from morpheus.database.db import get_session
from morpheus.database.util import row2dict
from morpheus.database.models.repository import Project, Commit
from morpheus.api.logic.coverage import MethodCoverageQuery, CommitQuery, ProjectQuery


ns = api.namespace(
    name='methods',
    description='Endpoint to obtain information about the methods within a given project.',
    authorization=False
)


################################################################ 
# Methods routes
################################################################

@ns.route('/<method_id>')
class SingleMethodRoute(Resource):
    
    @ns.response(200, 'Success')
    @ns.response(404, 'Method not found.')
    def get(self, method_id):
        Session = get_session()
        method = Session.query(ProdMethod) \
            .filter(ProdMethod.id == method_id)\
            .first()

        if method is None:
            return { "error": "Method not found..."}, 404

        return {"method": row2dict(method)}, 200

@ns.route('/project/<project_id>/')
class MethodsInProjectRoute(Resource):
    
    @ns.response(200, 'Success')
    @ns.response(404, 'Methods for project for given project id not found.')
    def get(self, project_id):
        Session = get_session()
        project = ProjectQuery.get_project(Session, project_id)

        if project is None:
            return {"error": f"Project '{project_id}' was not found..."}, 404

        methods = MethodCoverageQuery.get_methods(Session, project)

        if not methods:
            return {"methods": []}, 200

        return {
            "methods": list(map(row2dict, methods)),
        }, 200

@ns.route('/project/<project_id>/commits/<commit_id>/')
class MethodsInCommitRoute(Resource):
    
    @ns.response(200, 'Success')
    @ns.response(404, 'Methods for project for given project id or method id not found.')
    def get(self, project_id, commit_id):
        Session = get_session()
        project = ProjectQuery.get_project(Session, project_id)

        if project is None:
            return {"error": f"Project '{project_id}' was not found..."}, 404

        commit = CommitQuery.get_commit(Session, commit_id)
        
        if commit is None:
            return {"error": f"Commit with id '{commit_id}' was not found..."}, 404

        methods = MethodCoverageQuery.get_methods(Session, project, commit)

        if not methods:
            return {"methods": []}, 200

        return {
            "methods": list(map(row2dict, methods)),
        }, 200