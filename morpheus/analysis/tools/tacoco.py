"""
Script for running tacoco on a project
"""
import logging
import subprocess
from pathlib import Path
from morpheus.analysis.util.subject import AnalysisRepo
from morpheus.database.models.repository import Commit

logger = logging.getLogger(__name__)

class TacocoRunner():

    def __init__(self, repo: AnalysisRepo, output_dir: Path, tacoco_path: str, jdk: str = "13", log_file=subprocess.DEVNULL):
        self.__repo = repo
        self.project_path = repo.get_project_directory()
        self.tacoco_path = tacoco_path
        self.project_name = self.__repo.get_project_name()
        self.file_output_dir = output_dir / self.project_name
        self.log_file = log_file

    def run(self):
        if self.__run_tacoco_coverage() != 0:
            logger.error("Unable to obtain coverage...")
            raise RuntimeError("Unable to obtain coverage...")

        if self.__run_tacoco_analysis() != 0:
            logger.error("Unable to analyse exec file...")
            raise RuntimeError("Unable to analyse exec file...")

        if self.__run_tacoco_reader() != 0:
            logger.error("Unable to convert to readable format...")
            raise RuntimeError("Unable to convert to readable format...")
        
        return 0

    def __run_tacoco_coverage(self, debug=False):
        logging.info("[TACOCO] start coverage... %s", self.project_path)

        # Obtain commit sha
        commit: Commit = self.__repo.get_current_commit()

        path =  (self.file_output_dir / commit.sha).resolve()
        # Run analysis
        run_tacoco_coverage_cmd = f"""
        mvn exec:java \
            -Plauncher \
            -Dtacoco.sut={self.project_path} \
            -Dtacoco.home={self.tacoco_path} \
            -Dtacoco.project=coverage \
            -Dtacoco.outdir={path} \
            -Danalyzer.opts="configs/tacoco-analyzer.config" \
        """

        if debug:
            run_tacoco_coverage_cmd += " -Dtacoco.debug"

        # Store all logs per project per commit

        result = subprocess.run(run_tacoco_coverage_cmd, cwd=self.tacoco_path, stderr=self.log_file, stdout=self.log_file, shell=True)

        if  result.returncode != 0:
            raise RuntimeError(f"Command failed to run: {run_tacoco_coverage_cmd}")

        return 0

    def __run_tacoco_analysis(self):
        logging.info("[TACOCO] analyze coverage file: %s", self.project_path)

        # Obtain commit sha
        commit: Commit = self.__repo.get_current_commit()

        coverage_exec_path =  (self.file_output_dir / commit.sha / "coverage.exec").resolve()
        coverage_json_path =  (self.file_output_dir / commit.sha / "coverage.json").resolve()

        logger.debug("Tacoco Coverage Exec Path: %s", coverage_exec_path)
        logger.debug("Tacoco Coverage Json Path: %s", coverage_json_path)
        # Run analysis
        run_tacoco_analysis_cmd = f"""
        mvn exec:java \
            -Panalyzer \
            -Dtacoco.sut={self.project_path} \
            -Dtacoco.exec={coverage_exec_path} \
            -Dtacoco.json={coverage_json_path}
        """

        # Store all logs per project per commit
        result = subprocess.run(run_tacoco_analysis_cmd, cwd=self.tacoco_path, stderr=self.log_file, stdout=self.log_file, shell=True)
        if  result.returncode != 0:
                raise RuntimeError(f"Command failed to run: {run_tacoco_analysis_cmd}")

        return 0

    def __run_tacoco_reader(self):
        logging.info("[TACOCO] convert coverage to json: %s", self.project_path)

        commit: Commit = self.__repo.get_current_commit()

        coverage_json_path =  (self.file_output_dir / commit.sha / "coverage.json").resolve()

        run_tacoco_reader_cmd = f"""
        mvn exec:java \
            -Preader \
            -Dtacoco.json={coverage_json_path}
        """

        # Store all logs per project per commit
        result = subprocess.run(run_tacoco_reader_cmd, cwd=self.tacoco_path, stderr=self.log_file, stdout=self.log_file, shell=True)
        if  result.returncode != 0:
            raise RuntimeError(f"Command failed to run: {run_tacoco_reader_cmd}")

        return 0
