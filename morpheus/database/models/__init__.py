from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .methods import ProdMethod, ProdMethodVersion, TestMethod, LineCoverage
from .repository import Commit, Project