from flask_restx.resource import Resource
from morpheus.api.rest import api
from morpheus.database.db import Session, get_session
from morpheus.database.util import row2dict
from morpheus.database.models.methods import TestMethod
from morpheus.api.logic.coverage import ProjectQuery

ns = api.namespace(
    name='tests',
    description='Endpoint to obtain information about the tests within a given project.',   
    authorization=False
)

################################################################ 
# Test routes
#  - Obtain single test
#  - Obtain all tests within a single project
################################################################

@ns.route('/<test_id>', '/<test_id>/')
class SingleTestMethodRoute(Resource):
    
    @ns.response(200, 'Success')
    @ns.response(404, 'Method not found within given project and/or commit.')
    def get(self, test_id):
        test = Session.query(TestMethod) \
            .filter(TestMethod.id == test_id)\
            .first()

        if test is None:
            return { "error": "Method not found..."}, 404

        return {"test": row2dict(test)}, 200


@ns.route('/project/<project_id>', '/project/<project_id>/')
class TestMethodsInCommitRoute(Resource):
    
    @ns.response(200, 'Success')
    @ns.response(404, 'Methods for project for given project id or method id not found.')
    def get(self, project_id):
        Session = get_session()
        project = ProjectQuery.get_project(Session, project_id)

        if project is None:
            return {"error": f"Project '{project_id}' was not found..."}, 404

        tests = Session.query(TestMethod)\
            .filter(TestMethod.project_id == project_id)\
            .all()

        if not tests:
            return {"tests": []}, 200

        return {
            "tests": list(map(row2dict, tests)),
        }, 200
