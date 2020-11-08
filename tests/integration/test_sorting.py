import unittest
import pytest
import json
import os
from typing import List, Dict
from flask import jsonify
from spidertools.storage.parsing.tacoco import TacocoParser
from spidertools.storage.parsing.methods import MethodParser
from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.db_helper import DatabaseHelper
from spidertools.storage.query.querybuilder import MethodCoverageQuery
from spidertools.storage.query.output_formatter import coverage_format
from spidertools.storage.data.sorting import cluster

class TestQueryCoverageData(unittest.TestCase):

    def setUp(self):
        self.db_helper = DatabaseHelper(':memory:')
        self.resource_dir = f'.{os.path.sep}tests{os.path.sep}resources{os.path.sep}'

    def tearDown(self):
        pass

    def __init_database(self, project, commit):
        method_parser : MethodParser = MethodParser()
        methods_dict: List[Dict] = self.__load_methods(project.project_name, commit.sha)
        methods = method_parser\
            .set_commit(commit)\
            .parse(methods_dict)
        
        method_parser.store(self.db_helper, project, commit, methods)
        
        tacoco_parser : TacocoParser = TacocoParser()
        coverage_dict: Dict = self.__load_coverage(project.project_name, commit.sha)
        coverage = tacoco_parser\
            .parse(coverage_dict)

        tacoco_parser.store(self.db_helper, project, commit, coverage)

    def __load_coverage(self, project_name, commit_sha) -> List[Dict]:
        coverage_matrix_file = f'{self.resource_dir}{project_name}{os.path.sep}{commit_sha}-cov-matrix.json'
        with open(coverage_matrix_file) as coverage:
            return json.load(coverage)

    def __load_methods(self, project_name, commit_sha) -> List[Dict]:
        methods_file = f'{self.resource_dir}{project_name}{os.path.sep}methods-{commit_sha}.json'
        with open(methods_file) as methods:
            return json.load(methods)

    def test_querying_coverage_primitive_hamcrest(self):
        # Given: an initialized database
        project_name = 'primitive-hamcrest'
        commit_sha = '250f63fe6e70ca6c44ee696c1937b5ccb14f2e6e'

        project = Project(project_name=project_name)
        commit = Commit(sha=commit_sha)

        self.__init_database(project, commit)

        # When: we query a specific method
        with self.db_helper.create_session() as session:
            query = MethodCoverageQuery(session)\
                .set_commit(commit)\
                .set_project(project)

            methods = query.get_methods()
            tests = query.get_tests()
            edges = query.get_coverage()

        coverage = coverage_format(methods, tests, edges)

        coverage = cluster(coverage)

        assert coverage is not None
        assert json.dumps(coverage) is not None
