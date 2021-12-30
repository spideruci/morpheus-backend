import os
import logging
import json
from pathlib import Path
from typing import Tuple, List
from morpheus.analysis.util.subject import AnalysisRepo
from morpheus.analysis.tools import TacocoRunner
from morpheus.analysis.tools import MethodParserRunner
from morpheus.analysis.tools import ProjectBuilder
from morpheus.database.models import Commit, Project
from morpheus.config import Config
from morpheus.database.util import row2dict
from os.path import sep, exists
import shutil
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def _create_log_file(output_path: Path, commit_sha: str, log_name: str):
    log_dir = output_path / "logs" / commit_sha
    log_dir.mkdir(parents=True, exist_ok=True)

    log_filepath = log_dir / f"{log_name}.log"

    log_file = open(log_filepath, "w")

    try:
        yield log_file
    finally:
        log_file.close()


def run_analysis(url, output_path: Path, current, tags, commits, add_install=False):
    # Create output path if it doesn't exist:
    os.makedirs(output_path, exist_ok=True)

    with AnalysisRepo(url) as repo:
        project_name = repo.get_project_name()
        logger.info("Project: %s", project_name)

        # Add project
        project = Project(project_name=project_name)

        project_path = output_path / project_name

        os.makedirs(project_path, exist_ok=True)
        with open(project_path / "project.json", 'w') as f:
            f.write(json.dumps(row2dict(project)))

        if Config.TACOCO_HOME is None or Config.PARSER_HOME is None:
            logger.error("Please provide root folder of TACOCO and/or the Method Parser.")
            exit(1)

        # Get all commits we want to run the analysis on.
        commits_list: List[Commit] = []
        match (current, tags, commits):
            case (current, _, _ ) if current:
                commits_list = [repo.get_current_commit()]
            case (_, tags, _) if tags is not None:
                commits_list = repo.iterate_tagged_commits(tags)
            case (_, _, commits) if commits is not None:
                commits_list = repo.iterate_commits(commits)
            case _:
                raise RuntimeError("The run was misconfigured...")

        for commit in commits_list:
            logger.info("[INFO] Analyze commit: %s", commit.sha)

            # Setup analysis tools and add create their logging files.
            with _create_log_file(project_path, commit.sha, "tacoco") as tacoco_log, _create_log_file(project_path, commit.sha, "builder") as builder_log:

                builder = ProjectBuilder.get_builder(repo) \
                    .set_log_path(builder_log)

                tacoco_runner = TacocoRunner(repo, output_path, Config.TACOCO_HOME, log_file=tacoco_log)
                parser_runner = MethodParserRunner(repo, output_path, Config.PARSER_HOME)

                # Run analysis and return paths to output files
                try:
                    _analysis(repo, builder, tacoco_runner, parser_runner, output_path, add_install)
                except Exception as exc:
                    logger.error('Analysis for %s failed...', commit.sha)
                    logger.error('Exception %s', exc)
                    continue


def _analysis(repo: AnalysisRepo, builder: ProjectBuilder, tacoco_runner: TacocoRunner, parser_runner: MethodParserRunner, output_path: Path, add_install: bool) -> Tuple[str|None, str|None]:
    # Before each analysis remove all generated files of previous run
    repo.clean()

    # Combine data
    commit: Commit = repo.get_current_commit()
    output_path = output_path / repo.get_project_name() / commit.sha

    # Try compiling the project
    try:
        builder \
            .clean() \
            .compile() \
            .test_compile()
    except Exception as e:
        logger.error("%s", e)
        raise

    # Start analysis
    try:
        parser_runner.run()
        tacoco_runner.run()
    except Exception as e:
        logger.error("%s", e)

        if output_path.exists():
            shutil.rmtree(output_path)

        raise

    with open(output_path / "commits.json", 'w') as f:
        f.write(json.dumps(row2dict(commit)))

    logger.info("build successfull...")
    return (
        f"methods.json",
        f"coverage.json"
    )
