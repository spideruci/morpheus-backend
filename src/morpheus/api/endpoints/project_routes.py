from flask_restx.resource import Resource
from morpheus.api.rest import api
from morpheus.database.db import get_session
from morpheus.database.util import row2dict
from morpheus.database.models.repository import Project, Commit


ns = api.namespace(
    name='projects',
    description='Endpoint to obtain information about the projects.',
    authorization=False
)

################################################################ 
# Projects routes
################################################################ 
@ns.route('', '/')
class ProjectsRoute(Resource):

    @ns.doc(description="Obtain all projects.")
    @ns.response(200, "Success")
    @ns.response(404, "No projects in database")
    def get(self):
        Session = get_session()
        projects = Session.query(Project).all()

        if not projects:
            return {"error": "No projects in database"}, 404

        return {"projects": list(map(row2dict, projects))}, 200

@ns.route('/<project_id>', '/<project_id>/')
class ProjectRoute(Resource):

    @ns.doc(description="Get single project.", params={'project_id': 'Project identifier'})
    @ns.response(200, "Success")
    @ns.response(404, "Project was not found.")
    def get(self, project_id: int):
        Session = get_session()
        project = Session.query(Project)\
            .filter(Project.id==project_id)\
            .first()

        if project is None:
            return {"error": f"Project with id: {project_id} was not found."}, 404
        
        return {"project": row2dict(project)}, 200

    @ns.doc(False)
    def delete(self):
        # TODO implement delete functionality
        return {}, 501

    @ns.doc(False)
    def put(self):
        # TODO implement put functionality
        return {}, 501

################################################################ 
# Commits routes
################################################################ 
@ns.route('/<project_id>/commits', '/<project_id>/commits/')
@ns.doc(
        description='Retrieve all commits for given project id',
        param={'project_id': 'Project identifier'}
    )
class CommitsRoute(Resource):

    @ns.response(200, "Success")
    @ns.response(404, "Commit not found.")
    def get(self, project_id):
        Session = get_session()
        commits = Session.query(Commit) \
            .filter(Commit.project_id == project_id) \
            .all()

        if not commits:
            return {"error": f"no commits found for project_id '{project_id}'"}, 404

        return {"commits": list(map(row2dict, commits))}, 200

@ns.route('/<project_id>/commits/<commit_id>', '/<project_id>/commits/<commit_id>/')
@ns.doc(
    description='Retrieve a specific commit',
    param={
        'project_id': 'Project identifier',
        'commit_id': 'Commit identifier'
        }
    )
class CommitRoute(Resource):

    @ns.response(200, "Success")
    @ns.response(404, "Commit not found.")
    def get(self, project_id, commit_id):
        Session = get_session()
        commit = Session.query(Commit) \
            .filter(Commit.project_id == project_id) \
            .filter(Commit.id == commit_id) \
            .first()

        if commit is None:
            return {"error": f"no commit found for project id: '{project_id}' and commit id: '{commit_id}'"}, 404

        return {"commit": row2dict(commit)}, 200


