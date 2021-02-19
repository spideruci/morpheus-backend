import logging
from flask_restx import Api
from . import API_CONSTANTS
from sqlalchemy.orm.exc import NoResultFound

logger = logging.getLogger(__name__)

api: Api = Api(**API_CONSTANTS)

@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    logger.exception(message)

    return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    logger.warning("Database not found...")
    return {'message': 'A database result was required but none was found.'}, 404