from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from . import Base

class ProdMethod(Base):
    __tablename__ = 'prodmethods'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    method_name = Column(String, nullable=False)
    method_decl = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    package_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    
    # versions = relationship("ProdMethodVersion", backref=backref('method', uselist=False, lazy='dynamic'))

    UniqueConstraint(project_id, method_name, method_decl, class_name, package_name, file_path)

class ProdMethodVersion(Base):
    __tablename__ = 'method_versions'
    
    id = Column(Integer, primary_key=True)
    method_id = Column(Integer, ForeignKey('prodmethods.id'), nullable=False)
    commit_id = Column(Integer, ForeignKey('commits.id'), nullable=False)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)

    UniqueConstraint(method_id, commit_id, file_path, line_start, line_end)

class TestMethod(Base):
    __tablename__ = 'testcases'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    package_name = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    method_name = Column(String, nullable=False)

    # covered_lines = relationship("LineCoverage", backref=backref('testmethod', lazy='dynamic'))
    
    UniqueConstraint(project_id, package_name, method_name, class_name)

class LineCoverage(Base):
    __tablename__ = 'linecoverage'

    id = Column(Integer, primary_key=True)
    commit_id = Column(Integer, ForeignKey('commits.id'))
    test_id = Column(Integer, ForeignKey('testcases.id'))
    method_version_id = Column(Integer, ForeignKey('method_versions.id'))
    test_result = Column(Boolean, nullable=False)
    full_name = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    
    UniqueConstraint(commit_id, test_id, full_name, line_number)