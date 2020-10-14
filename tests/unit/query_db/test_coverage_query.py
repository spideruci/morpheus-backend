import unittest
import json
import os
from typing import List, Dict
from spidertools.storage.parsing.tacoco import TacocoParser
from spidertools.storage.parsing.methods import MethodParser
from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.db_helper import DatabaseHelper
from spidertools.storage.query.querybuilder import MethodCoverageQuery

class TestQueryCoverageData(unittest.TestCase):

    def setUp(self):
        self.project_name = 'mid_example'
        self.commit_sha = 'df1bc2481a05acc3944cc1c3f637856d54cd8ba8'
        self.project = Project(project_name=self.project_name)
        self.commit = Commit(sha=self.commit_sha)
        self.resource_dir = f'.{os.path.sep}tests{os.path.sep}resources{os.path.sep}'
        self.db_helper = DatabaseHelper(':memory:')

    def tearDown(self):
        pass

    def __init_database(self):
        method_parser : MethodParser = MethodParser()
        methods_dict: List[Dict] = self.__load_methods(self.project_name, self.commit_sha)
        methods = method_parser\
            .set_commit(self.commit)\
            .parse(methods_dict)
        
        method_parser.store(self.db_helper, self.project, self.commit, methods)
        
        tacoco_parser : TacocoParser = TacocoParser()
        coverage_dict: Dict = self.__load_coverage(self.project_name, self.commit_sha)
        coverage = tacoco_parser\
            .parse(coverage_dict)

        tacoco_parser.store(self.db_helper, self.project, self.commit, coverage)

    def __load_coverage(self, project_name, commit_sha) -> List[Dict]:
        coverage_matrix_file = f'{self.resource_dir}{project_name}{os.path.sep}{commit_sha}-cov-matrix.json'
        with open(coverage_matrix_file) as coverage:
            return json.load(coverage)

    def __load_methods(self, project_name, commit_sha) -> List[Dict]:
        methods_file = f'{self.resource_dir}{project_name}{os.path.sep}methods-{commit_sha}.json'
        with open(methods_file) as methods:
            return json.load(methods)

    def test_querying_all_prod_methods_of_a_commit(self):
        # Given: an initialized database
        self.__init_database()

        # When: we query a specific method
        with self.db_helper.create_session() as session_helper:
            session = session_helper.get_session()

            rows = MethodCoverageQuery(session)\
                .set_commit(self.commit)\
                .set_project(self.project)\
                .all()

        assert len(rows) == 6

    def test_querying_all_prod_methods_of_a_commit(self):
        # Given: an initialized database
        self.__init_database()

        # When: we query a specific method
        with self.db_helper.create_session() as session:
            query = MethodCoverageQuery(session)\
                .set_commit(self.commit)\
                .set_project(self.project)
            
            methods = query.get_methods()
            tests = query.get_tests()
            edges = query.get_coverage()

        assert len(methods) == 1
        assert len(tests) == 6
        assert len(edges) == 6