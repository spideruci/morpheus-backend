import sqlite3

# Abstact class
class TableHandler():
    def __init__(self, database_location: str):
        self._conn = sqlite3.connect(database_location)

    def execute(self, sql):
        c = self._conn.cursor()

        c.execute(sql)

        self._conn.commit()

        return c.fetchall()

    def close(self):
        self._conn.close()


class ProjectTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)
        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS Commits (
            project_id INT AUTO_INCREMENT
            url TEXT,
            organization TEXT,
            repo_name TEXT,
            FOREIGN KEY( project_id ) REFERENCES Projects ( project_id ),
            PRIMARY KEY( project_id, commit_sha )
        );
        """

        self.execute(CREATE_TABLE)

class CommitTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)
        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS Commits (
            commit_id INT AUTO_INCREMENT,
            project_id INT,
            commit_sha TEXT NOT NULL UNIQUE,
            FOREIGN KEY( project_id ) REFERENCES Projects ( project_id ),
            PRIMARY KEY( project_id, commit_sha )
        );
        """

        self.execute(CREATE_TABLE)

class BuildTableHandler(TableHandler):
    def __init__(self, database_location):
        super().__init__(database_location)

        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS BuildResults (
            commit_sha TEXT,
            build_passed BOOLEAN,
            FOREIGN KEY ( commit_sha ) REFERENCES Commit( commit_sha ),
            PRIMARY KEY ( project_id, commit_sha )
        );
        """

        self.execute(CREATE_TABLE)