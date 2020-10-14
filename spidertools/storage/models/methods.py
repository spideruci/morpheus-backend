from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from . import Base

class ProdMethod(Base):
    __tablename__ = 'prodmethods'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    method_name = Column(String)
    method_decl = Column(String)
    class_name = Column(String)
    package_name = Column(String)
    file_path = Column(String)
    
    versions = relationship("ProdMethodVersion", backref=backref('method', uselist=False))

    UniqueConstraint(project_id, method_name, method_decl, class_name, package_name)

class ProdMethodVersion(Base):
    __tablename__ = 'method_versions'
    
    id = Column(Integer, primary_key=True)
    method_id = Column(Integer, ForeignKey('prodmethods.id'))
    commit_id = Column(Integer, ForeignKey('commits.id'))
    line_start = Column(Integer)
    line_end = Column(Integer)

    UniqueConstraint(method_id, commit_id, line_start, line_end)

class TestMethod(Base):
    __tablename__ = 'testcases'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    class_name = Column(String)
    method_name = Column(String)

    covered_lines = relationship("LineCoverage", backref='testmethod')
    
    UniqueConstraint(project_id, method_name, class_name)

# class TestResult(Base):
#     __tablename__ = 'testresults'

#     id = Column(Integer, primary_key=True)
#     test_id = Column(Integer, ForeignKey('testcases.id'))
#     commit_id = Column(Integer, ForeignKey('commits.id'))
#     test_result = Column(Boolean)

#     coverage = relationship("LineCoverage", backref='testresult')

#     UniqueConstraint(test_id, commit_id)

# class LineCoverage(Base):
#     __tablename__ = 'line_coverage'

#     id = Column(Integer, primary_key=True)
#     test_result_id = Column(Integer, ForeignKey('testresults.id'))
#     method_version_id = Column(Integer, ForeignKey('method_versions.id'))
#     full_name = Column(String, nullable=False)
#     line_number = Column(Integer, nullable=False)
    
#     UniqueConstraint(test_result_id, full_name, line_number)

class LineCoverage(Base):
    __tablename__ = 'linecoverage'

    id = Column(Integer, primary_key=True)
    commit_id = Column(Integer, ForeignKey('commits.id'))
    test_id = Column(Integer, ForeignKey('testcases.id'))
    method_version_id = Column(Integer, ForeignKey('method_versions.id'))
    test_result = Column(Boolean)
    full_name = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    
    UniqueConstraint(commit_id, test_id, method_version_id, line_number)