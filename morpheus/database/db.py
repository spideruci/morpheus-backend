from morpheus.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = None
Session = None

def get_session():
    global Session
    return Session

def get_engine():
    global engine
    return engine

def create_engine_and_session():
    global engine 
    global Session

    engine = create_engine(f"{Config.SQLALCHEMY_DATABASE_TYPE}{Config.DATABASE_PATH}")
    Session = scoped_session(sessionmaker(bind=engine))

    return (engine, Session)



def init_db(engine):
    import morpheus.database.models.repository
    import morpheus.database.models.methods
    from morpheus.database.models import Base

    Base.metadata.create_all(bind=engine)
