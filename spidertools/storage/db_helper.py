from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.sqltypes import Boolean
from spidertools.storage.models import Base
from spidertools.storage.models.repository import Project, Commit
from spidertools.storage.models.methods import TestMethod, ProdMethod, ProdMethodVersion, LineCoverage
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from typing import List, Tuple

class DatabaseHelper():
    def __init__(self, db_path, echo=False):
        self.engine = create_engine(f'sqlite:///{db_path}', echo=echo)

        # Create Tables if not exist
        Project.__table__.create(bind=self.engine, checkfirst=True)
        Commit.__table__.create(bind=self.engine, checkfirst=True)

        # Method tables
        ProdMethod.__table__.create(bind=self.engine, checkfirst=True)
        ProdMethodVersion.__table__.create(bind=self.engine, checkfirst=True)

        # Test code / Coverage
        TestMethod.__table__.create(bind=self.engine, checkfirst=True)
        LineCoverage.__table__.create(bind=self.engine, checkfirst=True)

    def query(self, obj: Base):
        # TODO Create a cleaner wrapper around query...
        session = Session(self.engine, expire_on_commit=False)
        return session.query(obj)
    
    def create_session(self) -> 'DatabaseSession':
        return DatabaseSession(self.engine)

class DatabaseSession():
    def __init__(self, engine):
        self.engine = engine
        self.session = Session(self.engine,  expire_on_commit=False)

    def __enter__(self):
        if self.session is None:
            self.session = Session(self.engine,  expire_on_commit=False)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.session.commit()
        self.session = self.session.close()

    def add(self, object: Base) -> Tuple[Base, Boolean]:
        result = True

        try:
            self.session.add(object)
            self.session.flush()
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            result = False
            object = self.session.query(type(object))\
                .filter_by(**row2dict(object))\
                .first()

        return object, result

    def query(self, obj: Base):
        return self.session.query(obj)

    def add_all(self, object: List[Base]):
        map(self.add, object)

    def get_session(self):
        return self.session

    def flush(self):
        self.session.flush()

    def close(self):
        self.session.close()

def row2dict(row, ignore_none=False):
    d = {}
    for column in row.__table__.columns:
        if (value := getattr(row, column.name)) is not None:
            d[column.name] = str(value)

    return d
