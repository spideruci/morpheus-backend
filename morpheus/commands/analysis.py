import os
import logging
import json
from pathlib import Path
from typing import Tuple, List
from morpheus.analysis.util.subject import AnalysisRepo
from morpheus.analysis.tools import TacocoRunner, tacoco
from morpheus.analysis.tools import MethodParserRunner
from morpheus.database.models import Commit, Project
from morpheus.config import Config
from morpheus.database.util import row2dict
from os.path import sep, exists

logger = logging.getLogger(__name__)

def run_analysis(url, output_path: Path, current, tags, commits, add_install=False):

    if not os.path.exists(output_path):
        logger.warning(f'Output path did not exists: {output_path}, so it was created.')
        os.makedirs(output_path)

    with AnalysisRepo(url) as repo:
        logger.info("Project: %s", repo.get_project_name())

        # Add project
        project = Project(project_name=repo.get_project_name())

        project_path = output_path / repo.get_project_name()

        if not exists(project_path):
            os.makedirs(project_path)
        with open(f"{project_path}{sep}project.json", 'w') as f:
            f.write(json.dumps(row2dict(project)))

        if Config.TACOCO_HOME is None or Config.PARSER_HOME is None:
            logger.error("Please provide root folder of TACOCO and/or the Method Parser.")
            exit(1)

        # Analysis tools
        tacoco_runner = TacocoRunner(repo, output_path, Config.TACOCO_HOME)
        parser_runner = MethodParserRunner(repo, output_path, Config.PARSER_HOME)

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

            # Run analysis and return paths to output files
            success, method_file_path, tacoco_file_path = _analysis(repo, tacoco_runner, parser_runner, output_path, add_install)
            
            if not success:
                logger.error('Analysis for %s failed...', commit.sha)
                continue
            else:
                logger.info(f'Output per file: \n\tMethod File: {method_file_path}\n\tTacoco File: {tacoco_file_path}')

def _analysis(repo: AnalysisRepo, tacoco_runner: TacocoRunner, parser_runner: MethodParserRunner, output_path: Path, add_install: bool) -> Tuple[bool, str, str]:
    # Before each analysis remove all generated files of previous run
    repo.clean()

    # Try compiling the project
    try:
        if not add_install:
            tacoco_runner \
                .compile() \
                .test_compile()
        else:
            tacoco_runner \
                .install() \
                .compile() \
                .test_compile()
    except Exception as e:
        logger.error("%s", e)
        return (False, None, None)

    # Start analysis
    parser_runner.run()
    tacoco_runner.run()

    # Combine data
    commit: Commit = repo.get_current_commit()

    output_path = output_path / repo.get_project_name() / commit.sha

    with open(output_path / "commits.json", 'w') as f:
            f.write(json.dumps(row2dict(commit)))

    logger.info("build successfull...")
    return (True,
        f"methods.json",
        f"coverage.json"
    )
