"""
Script for obtaining method signature on a project
"""
import os
import logging
from pathlib import Path
from subprocess import Popen
from morpheus.analysis.util.subject import AnalysisRepo
from morpheus.database.models.repository import Commit

logger = logging.getLogger(__name__)

class MethodParserRunner():

    def __init__(self, repo: AnalysisRepo, output_dir: Path, history_slicer_path: str):
        self.__repo = repo
        self.project_path = repo.get_project_directory()
        self.history_slicer_path = history_slicer_path
        self.project_name = self.__repo.get_project_name()
        self.file_output_dir = output_dir / self.project_name

    def run(self):
        logger.info("[Method Parser] start analysis... %s", self.project_path)
        
        # Obtain commit sha
        commit: Commit = self.__repo.get_current_commit()

        # Run analysis
        run_method_parser_cmd = f"""
        ./gradlew method-parser:run --args="--sut {self.project_path} --outputPath {self.file_output_dir}{os.path.sep}{commit.sha}{os.path.sep}methods.json"
        """

        p = Popen(run_method_parser_cmd, cwd=self.history_slicer_path, shell=True)
        return p.wait()