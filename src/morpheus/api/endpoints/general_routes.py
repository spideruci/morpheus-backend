from morpheus.api.rest import api
from flask_restx.resource import Resource


ns = api.namespace(
    name='health',
    description='Health endpoint.',   
    authorization=False
)


@ns.route('', '/')
class HeatlhRoute(Resource):
    @ns.response(200, 'Success')
    @ns.response(503, 'Server is not up yet.')
    def get(self):
        return {}, 200