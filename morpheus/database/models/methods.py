from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.schema import Index
from . import Base


class ProdMethod(Base):
    __tablename__ = 'prodmethods'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    method_name = Column(String, nullable=False)
    method_decl = Column(String, nullable=False, index=True)
    class_name = Column(String, nullable=False, index=True)
    package_name = Column(String, nullable=False, index=True)

    UniqueConstraint(project_id, package_name, class_name, method_decl)


class ProdMethodVersion(Base):
    __tablename__ = 'method_versions'
    
    id = Column(Integer, primary_key=True)
    method_id = Column(Integer, ForeignKey('prodmethods.id'), index=True, nullable=False)
    commit_id = Column(Integer, ForeignKey('commits.id'), index=True, nullable=False)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)

    UniqueConstraint(method_id, commit_id, file_path)

    def __str__(self):
        return f"{self.id} {self.method_id} {self.commit_id} {self.line_start} {self.line_end} {self.file_path}"

class TestMethod(Base):
    __tablename__ = 'testcases'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    package_name = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    method_name = Column(String, nullable=False)

    UniqueConstraint(project_id, package_name, class_name, method_name)


class LineCoverage(Base):
    __tablename__ = 'linecoverage'

    id = Column(Integer, primary_key=True)
    commit_id = Column(Integer, ForeignKey('commits.id'), index=True)
    test_id = Column(Integer, ForeignKey('testcases.id'), index=True)
    method_version_id = Column(Integer, ForeignKey('method_versions.id'), index=True)
    test_result = Column(Boolean, nullable=False)
    full_name = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    
    UniqueConstraint(commit_id, test_id, method_version_id, line_number)

    @declared_attr
    def __table_args__(cls):
        return (
            Index('test_history_edge_idx_%s' % cls.__tablename__, 'commit_id', 'method_version_id', 'test_result'),
            Index('test_history_edge_sort_idx_%s' % cls.__tablename__, 'method_version_id', 'commit_id'),
            Index('method_history_edge_sort_idx_%s' % cls.__tablename__, 'method_version_id', 'test_id'),
        )