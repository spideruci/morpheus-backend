from pathlib import Path
from morpheus.database.db import create_engine_and_session, init_db
from morpheus.commands.db import add_project

RESOURCE_PATH = Path("./tests/resources/")

def store(project_path: Path):
    engine, session = create_engine_and_session()
    init_db(engine)

    add_project(session, project_path.name, project_path)

    session.close()


def test_benchmark_inserting_coverage(benchmark):
    project = "commons-cli"
    project_path = RESOURCE_PATH / project

    benchmark(store, project_path)
