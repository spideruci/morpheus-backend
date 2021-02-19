from morpheus.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(f"{Config.SQLALCHEMY_DATABASE_TYPE}{Config.DATABASE_PATH}")
Session = scoped_session(sessionmaker(bind=engine))


def init_db(engine):
    import morpheus.database.models.repository
    import morpheus.database.models.methods
    from morpheus.database.models import Base

    Base.metadata.create_all(bind=engine)