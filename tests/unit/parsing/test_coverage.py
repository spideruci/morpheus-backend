import unittest
import json
import os
from typing import List, Dict
from spidertools.storage.parsing.tacoco import TacocoParser
from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.models.methods import LineCoverage
from spidertools.storage.db_helper import DatabaseHelper


class TestCoverageParser(unittest.TestCase):
    def setUp(self):
        self.resource_dir = f'.{os.path.sep}tests{os.path.sep}resources{os.path.sep}'
        self.db_helper = DatabaseHelper(':memory:')

    def tearDown(self):
        pass

    def load_coverage(self, project_name, commit_sha) -> List[Dict]:
        coverage_matrix_file = f'{self.resource_dir}{project_name}{os.path.sep}{commit_sha}-cov-matrix.json'
        with open(coverage_matrix_file) as coverage:
            return json.load(coverage)

    def test_parsing_coverage(self):
        # Given: some coverage information
        project_name = 'mid_example'
        commit_sha = 'df1bc2481a05acc3944cc1c3f637856d54cd8ba8'

        commit = Commit(sha=commit_sha)
        coverage: Dict = self.load_coverage(project_name, commit_sha)

        # When parsing the coverage file
        parser : TacocoParser = TacocoParser()

        output = parser\
            .parse(coverage)

        assert len(output) == 6
