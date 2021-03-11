from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import DateTime
from . import Base

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    project_name = Column(String, nullable=False)
    
    UniqueConstraint(project_name)

    # commits = relationship("Commit", backref=backref('project', lazy='dynamic'))
    # methods = relationship("ProdMethod", backref=backref('project', lazy='dynamic'))
    # tests = relationship("TestMethod", backref=backref('project', lazy='dynamic'))

    def __repr__(self):
        return f"<Project(id='{self.id}', project_name={self.project_name})>"

class Commit(Base):
    __tablename__ = 'commits'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    sha = Column(String, nullable=False)
    author = Column(String, nullable=False)
    datetime = Column(String, nullable=False)

    # test_results = relationship("LineCoverage", backref=backref('commit', lazy='dynamic'))
    # prod_method_versions = relationship("ProdMethodVersion", backref('commit', lazy='dynamic'))
    
    UniqueConstraint(project_id, sha)

    def __repr__(self):
        return f"<Commit(project_id='{self.project_id}', sha={self.sha}, author={self.author}, datetime={self.datetime})>"