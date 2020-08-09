import sqlite3

# Abstact class
class TableHandler():
    def __init__(self, database_location: str):
        self._conn = sqlite3.connect(database_location)

    def create(self, sql):
        c = self._conn.cursor()
        c.execute(sql)
        self._conn.commit()

    def select(self, sql, values=()):
        c = self._conn.cursor()
        c.execute(sql, values)
        return c.fetchone()


    def insert(self, sql, values=()):
        c = self._conn.cursor()
        c.execute(sql, values)
        self._conn.commit()


    def close(self):
        self._conn.close()


class ProjectTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)
        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS Projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT
        );
        """

        self.create(CREATE_TABLE)

    def add_project(self, project_name):
        self.insert('''INSERT INTO Projects( project_name ) VALUES (?) ''', (project_name, ))

    def get_project_id(self, project_name) -> int:
        return self.select('''SELECT project_id FROM Projects WHERE project_name=?''', (project_name, ))[0]

class CommitTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)
        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS Commits (
            commit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            commit_sha TEXT NOT NULL,
            FOREIGN KEY( project_id ) REFERENCES Projects ( project_id )
        );
        """

        self.create(CREATE_TABLE)

    def add_commit(self, project_id, commit_sha):
        self.insert('''INSERT INTO Commits( project_id, commit_sha ) VALUES (?, ?) ''', (project_id, commit_sha))

    def get_commit_id(self, project_id, commit_sha):
        return self.select('''SELECT commit_id FROM Commits WHERE project_id=? AND commit_sha=?''', (project_id, commit_sha))[0]

class BuildTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)

        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS BuildResults (
            commit_id INTEGER,
            build_passed BOOLEAN,
            FOREIGN KEY ( commit_id ) REFERENCES Commits( commit_id ),
            PRIMARY KEY ( commit_id )
        );
        """

        self.create(CREATE_TABLE)

    def add_build_result(self, commit_id: int, build_passed: bool):
        self.insert('''INSERT INTO BuildResults( commit_id, build_passed ) VALUES (?, ?) ''', (commit_id, build_passed))

class ProductionMethodTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)

        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS ProductionMethods (
            method_id INTEGER PRIMARY KEY AUTOINCREMENT,
            method_name TEXT,
            class_name TEXT,
            package_name TEXT,
            commit_id INTEGER,
            FOREIGN KEY ( commit_id ) REFERENCES Commits( commit_id )
        );
        """
        self.create(CREATE_TABLE)

    def add_production_method(self, method_name: str, class_name: str, package_name: str, commit_id: int):
        self.insert('''INSERT INTO ProductionMethods( method_name, class_name, package_name, commit_id ) VALUES (?, ?, ?, ?) ''', (method_name, class_name, package_name, commit_id))

    def get_method_id(self, method_name, class_name, package_name, commit_id):
        return self.select('''
            SELECT method_id FROM ProductionMethods 
            WHERE method_name=? 
            AND class_name=?
            AND package_name=?
            AND commit_id=?
        
        ''', (method_name, class_name, package_name, commit_id))[0] 
    
    def get_all_methods(self, project_id, commit_id):
        pass

class TestMethodTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)

        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS TestMethods (
            commit_id INTEGER,
            test_id INTEGER,
            test_name TEXT,
            FOREIGN KEY ( commit_id ) REFERENCES Commits( commit_id ),
            PRIMARY KEY ( commit_id, test_id )
        );
        """
        self.create(CREATE_TABLE)

    def add_test_method(self, test_id: int, test_name: str, commit_id: int):
        self.insert('''INSERT INTO TestMethods( test_id, test_name, commit_id ) VALUES (?, ?, ?) ''', (test_id, test_name, commit_id))

    def get_all_methods(self, project_id, commit_id):
        pass

class MethodCoverageTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)

        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS MethodCoverage (
            method_id INTEGER,
            test_id INTEGER,
            commit_id TEXT,
            FOREIGN KEY ( commit_id ) REFERENCES Commits( commit_id ),
            FOREIGN KEY ( test_id ) REFERENCES Commits( commit_id ),
            FOREIGN KEY ( method_id ) REFERENCES Commits( commit_id ),
            PRIMARY KEY (method_id, test_id, commit_id)
        );
        """
        self.create(CREATE_TABLE)
    
    def add_coverage(self, method_id, test_id, commit_id):
        self.insert('''INSERT INTO MethodCoverage ( method_id, test_id, commit_id ) VALUES (?, ?, ?) ''', (method_id, test_id, commit_id))

    def get_all_methods(self, project_id, commit_id):
        pass

class MethodCoverageHandler():

    def __init__(self, database_location):
        self.prod_method_table = ProductionMethodTableHandler(database_location)
        self.test_method_table = TestMethodTableHandler(database_location)
        self.cov_method_table = MethodCoverageTableHandler(database_location)

    def add_project_coverage(self, project_id: int, commit_id: str, prod_methods, test_methods):

        for method in prod_methods:
            self.prod_method_table.add_production_method(method["methodName"], method["className"], method["packageName"], commit_id)

        for method in test_methods:
            self.test_method_table.add_test_method(method["test_id"], method["test_name"], commit_id)
        
        for method in prod_methods:
            method_id = self.prod_method_table.get_method_id(method["methodName"], method["className"], method["packageName"], commit_id)
            
            for test_id in method['test_ids']:
                self.cov_method_table.add_coverage(method_id, test_id, commit_id)
    
    def get_project_coverage(self, project_id: int, commit_id: str):
        return {
            'methods': self.prod_method_table.get_all_methods(project_id, commit_id),
            'tests': self.test_method_table.get_all_methods(project_id, commit_id),
            'links': self.prod_method_table.get_all_coverage(project_id, commit_id)
        }