from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from . import Base

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    project_name = Column(String, nullable=False)
    
    UniqueConstraint(project_name)

    commits = relationship("Commit", backref='project')
    methods = relationship("ProdMethod", backref='project')
    tests = relationship("TestMethod", backref='project')

    def __repr__(self):
        return f"<Project(id='{self.id}', project_name={self.project_name})>"

class Commit(Base):
    __tablename__ = 'commits'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    sha = Column(String)

    test_results = relationship("LineCoverage", backref='commit')
    prod_method_versions = relationship("ProdMethodVersion", backref='commit')
    
    UniqueConstraint(project_id, sha)

    def __repr__(self):
        return f"<Commit(project_id='{self.project_id}', sha={self.sha})>"