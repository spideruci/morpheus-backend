from typing import Tuple
from sqlalchemy.engine.base import Engine
from morpheus.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session


engine: Engine
session: Session

def get_session() -> Session:
    global session

    if session is None:
        raise RuntimeError("Session was not initialized")

    return session

def get_engine():
    global engine

    if engine is None:
        raise RuntimeError("Session was not initialized")

    return engine

def create_engine_and_session() -> Tuple[Engine, Session]:
    global engine 
    global session

    engine = create_engine(f"{Config.SQLALCHEMY_DATABASE_TYPE}{Config.DATABASE_PATH}")
    session = scoped_session(sessionmaker(bind=engine))

    return (engine, session)



def init_db(engine):
    import morpheus.database.models.repository
    import morpheus.database.models.methods
    from morpheus.database.models import Base

    Base.metadata.create_all(bind=engine)
