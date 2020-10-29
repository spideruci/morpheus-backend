import unittest
import json
import os
from typing import List, Dict, Tuple
from spidertools.storage.parsing.methods import MethodParser
from spidertools.storage.models.repository import Commit, Project
from spidertools.storage.models.methods import ProdMethod, ProdMethodVersion
from spidertools.storage.db_helper import DatabaseHelper


class TestMethodParser(unittest.TestCase):
    def setUp(self):
        self.resource_dir = f'.{os.path.sep}tests{os.path.sep}resources{os.path.sep}'
        self.db_helper = DatabaseHelper(':memory:')

    def tearDown(self):
        pass

    def load_methods(self, project_name, commit_sha) -> List[Dict]:
        methods_file = f'{self.resource_dir}{project_name}{os.path.sep}methods-{commit_sha}.json'
        with open(methods_file) as methods:
            return json.load(methods)

    def test_parsing_methods(self):
        # Given: some coverage information
        project_name = 'mid_example'
        commit_sha = 'df1bc2481a05acc3944cc1c3f637856d54cd8ba8'
        commit = Commit(sha=commit_sha)

        methods: List[Dict] = self.load_methods(project_name, commit_sha)

        # When parsing the coverage file
        parser : MethodParser = MethodParser().set_commit(commit)

        # Then: It contain 1 methods (The test methods are filtered out.)
        results = parser.parse(methods)
        assert len(results) == 1


    def test_adding_single_project_with_two_commits_to_database(self):
        # Given: some coverage information
        # Project 1
        name = 'mid_example'
        url = 'https://github.com/jajones/mid_example'
        
        commit_sha = 'df1bc2481a05acc3944cc1c3f637856d54cd8ba8'
        methods_dict: List[Dict] = self.load_methods(name, commit_sha)

        # Init project and commits
        project = Project(project_name=name)
        commit1 = Commit(sha='commit-1')
        commit2 = Commit(sha='commit-2')

        # First add project, and then commits        
        with self.db_helper.create_session() as session:
            session.add(project)

            project.commits.append(commit1)
            project.commits.append(commit2)
            session.add_all([commit1, commit2])

            parser : MethodParser = MethodParser()
            methods1: List[Tuple[ProdMethod, ProdMethodVersion]] = parser.set_commit(commit1).parse(methods_dict)

            for method, version in methods1:
                method.project = project
                method, _ = session.add(method)

                version.method = method
                session.add(version)

            methods2: List[Tuple[ProdMethod, ProdMethodVersion]] = parser.set_commit(commit2).parse(methods_dict)

            for method, version in methods2:
                method.project = project
                method, _ = session.add(method)

                version.method = method
                session.add(version)
                
        assert len(self.db_helper.query(Project).all()) == 1
        assert len(self.db_helper.query(Commit).all()) == 2
        assert len(self.db_helper.query(ProdMethod).all()) == 1
        assert len(self.db_helper.query(ProdMethodVersion).all()) == 2



    def test_adding_two_projects_to_database(self):
        # Given: some coverage information
        # Project 1
        name = 'mid_example'        
        commit_sha = 'df1bc2481a05acc3944cc1c3f637856d54cd8ba8'
        methods_dict: List[Dict] = self.load_methods(name, commit_sha)

        parser: MethodParser = MethodParser()

        # Init project and commits
        project1 = Project(project_name='p1')
        commit1 = Commit(sha='commit-1')
        methods1: List[Tuple[ProdMethod, ProdMethodVersion]] = parser\
            .set_commit(commit1)\
            .parse(methods_dict)

        project2 = Project(project_name='p2')
        commit2 = Commit(sha='commit-2')
        methods2: List[Tuple[ProdMethod, ProdMethodVersion]] = parser\
            .set_commit(commit2)\
            .parse(methods_dict)

        # When storing the data in the database
        parser.store(self.db_helper, project1, commit1, methods1)
        parser.store(self.db_helper, project2, commit2, methods2)
                
        # Then: 
        assert len(self.db_helper.query(Project).all()) == 2
        assert len(self.db_helper.query(Commit).all()) == 2
        assert len(self.db_helper.query(ProdMethod).all()) == 2
        assert len(self.db_helper.query(ProdMethodVersion).all()) == 2

