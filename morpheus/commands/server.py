import logging
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from morpheus.api.rest import api
from morpheus.api.endpoints.project_routes import ns as project_namespace
from morpheus.api.endpoints.methods_routes import ns as methods_routes
from morpheus.api.endpoints.tests_routes import ns as tests_namespace
from morpheus.api.endpoints.coverage_routes import ns as coverage_namespace
from morpheus.config import Config

from morpheus.database.db import create_engine_and_session, init_db

logger = logging.getLogger(__name__)

def create_morpheus_backend(database: Path):
    app =  Flask(__name__)
    CORS(app)
    
    Config.DATABASE_PATH = database.resolve()
    (engine, Session) = create_engine_and_session()
    init_db(engine)

    # Add routes
    api.init_app(app)
    api.add_namespace(project_namespace)
    api.add_namespace(methods_routes)
    api.add_namespace(tests_namespace)
    api.add_namespace(coverage_namespace)

    # Remove database after using it.
    @app.teardown_appcontext
    def teardown_db(resp_or_exc):
        Session.remove()

    return app

def start_morpheus_backend(database: Path, host, port, debug=True):

    
    app = create_morpheus_backend(database)

    app.run(
        host=str(host),
        port=port,
        debug=debug
    )