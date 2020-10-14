import unittest
import json
import os
from typing import List, Dict
from spidertools.storage.parsing.tacoco import TacocoParser
from spidertools.storage.parsing.methods import MethodParser
from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.models.methods import LineCoverage
from spidertools.storage.db_helper import DatabaseHelper


class TestCoverageAndMethodParser(unittest.TestCase):
    def setUp(self):
        self.resource_dir = f'.{os.path.sep}tests{os.path.sep}resources{os.path.sep}'
        self.db_helper = DatabaseHelper(':memory:')

    def tearDown(self):
        pass

    def load_coverage(self, project_name, commit_sha) -> List[Dict]:
        coverage_matrix_file = f'{self.resource_dir}{project_name}{os.path.sep}{commit_sha}-cov-matrix.json'
        with open(coverage_matrix_file) as coverage:
            return json.load(coverage)

    def load_methods(self, project_name, commit_sha) -> List[Dict]:
        methods_file = f'{self.resource_dir}{project_name}{os.path.sep}methods-{commit_sha}.json'
        with open(methods_file) as methods:
            return json.load(methods)

    def test_parsing_and_storing_coverage_data(self):
        # Given: some coverage information
        project_name = 'mid_example'
        commit_sha = 'df1bc2481a05acc3944cc1c3f637856d54cd8ba8'

        project = Project(project_name=project_name)
        commit = Commit(sha=commit_sha)

        # When
        method_parser : MethodParser = MethodParser()
        methods_dict: List[Dict] = self.load_methods(project_name, commit_sha)
        methods = method_parser\
            .set_commit(commit)\
            .parse(methods_dict)
        
        method_parser.store(self.db_helper, project, commit, methods)
        
        tacoco_parser : TacocoParser = TacocoParser()
        coverage_dict: Dict = self.load_coverage(project_name, commit_sha)
        coverage = tacoco_parser\
            .parse(coverage_dict)

        tacoco_parser.store(self.db_helper, project, commit, coverage)

        assert len(self.db_helper.query(LineCoverage).all()) != 0