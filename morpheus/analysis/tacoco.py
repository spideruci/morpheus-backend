"""
Script for running tacoco on a project
"""
import os
import logging
from subprocess import Popen
from morpheus.analysis.util.subject import AnalysisRepo
from morpheus.database.models.repository import Commit

logger = logging.getLogger(__name__)

class TacocoRunner():

    def __init__(self, repo: AnalysisRepo, output_dir: str, tacoco_path: str, jdk: str = "13"):
        self.__repo = repo
        self.project_path = repo.get_project_directory()
        self.tacoco_path = tacoco_path
        self.project_name = self.__repo.get_project_name()
        self.file_output_dir = output_dir + os.path.sep + self.project_name

    def install(self):
        logger.info("[TACOCO] start builder on: %s", self.project_path)

        cmd = [f"mvn install"]
        success = self.__run_command(cmd)

        if success == 1:
            raise Exception("'mvn install' failed...")

        return self

    def compile(self):
        logger.info("[TACOCO] start builder on: %s", self.project_path)

        cmd = [f"mvn compile"]
        success = self.__run_command(cmd)

        if success == 1:
            raise Exception("'mvn compile' failed...")

        return self

    def test_compile(self):
        logger.info("[TACOCO] start builder on: %s", self.project_path)

        cmd = [f"mvn test-compile"]
        success = self.__run_command(cmd)

        if success == 1:
            raise Exception("'mvn test-compile' failed...")

        return self

    def __run_command(self, cmd):
        logger.info("[TACOCO] Run command on: %s", self.project_path)

        # If tacoco was already run before it places a classpath in the root directory
        # which causes problems for a rerun for some checks (apache-rat-plugin).
        p = Popen(["rm", "tacoco.cp"], cwd=self.project_path)
        p.wait()
        my_env = os.environ.copy()

        logger.debug("[TACOCO] command run: %s", cmd)
        p = Popen(cmd, cwd=self.project_path, shell=True, env=my_env)

        return p.wait()

    def run(self):
        if self.__run_tacoco_coverage() != 0:
            logger.error("Unable to obtain coverage...")
            return 1

        if self.__run_tacoco_analysis() != 0:
            logger.error("Unable to analyse exec file...")
            return 1
        
        if self.__run_tacoco_reader() != 0:
            logger.error("Unable to convert to readable format...")
            return 1
        
        return 0

    def __run_tacoco_coverage(self, debug=False):
        logging.info("[TACOCO] start coverage... %s", self.project_path)

        # Obtain commit sha
        commit: Commit = self.__repo.get_current_commit()

        # Run analysis
        run_tacoco_coverage_cmd = f"""
        mvn exec:java \
            -Plauncher \
            -Dtacoco.sut={self.project_path} \
            -Dtacoco.home={self.tacoco_path} \
            -Dtacoco.project=coverage \
            -Dtacoco.outdir={self.file_output_dir}{os.path.sep}{commit.sha} \
            -Danalyzer.opts="configs/tacoco-analyzer.config" \
        """

        if debug:
            run_tacoco_coverage_cmd += " -Dtacoco.debug"

        p = Popen(run_tacoco_coverage_cmd, cwd=self.tacoco_path, shell=True)
        return p.wait()

    def __run_tacoco_analysis(self):
        logging.info("[TACOCO] start analysis for: %s", self.project_path)

        # Obtain commit sha
        commit: Commit = self.__repo.get_current_commit()

        # Run analysis
        run_tacoco_analysis_cmd = f"""
        mvn exec:java \
            -Panalyzer \
            -Dtacoco.sut={self.project_path} \
            -Dtacoco.exec={self.file_output_dir}{os.path.sep}{commit.sha}{os.path.sep}coverage.exec \
            -Dtacoco.json={self.file_output_dir}{os.path.sep}{commit.sha}{os.path.sep}coverage.json
        """

        p = Popen(run_tacoco_analysis_cmd, cwd=self.tacoco_path, shell=True)
        return p.wait()

    def __run_tacoco_reader(self):
        logging.info("[TACOCO] start reader for: %s", self.project_path)

        commit: Commit = self.__repo.get_current_commit()

        run_tacoco_reader_cmd = f"""
        mvn exec:java \
            -Preader \
            -Dtacoco.json={self.file_output_dir}{os.path.sep}{commit.sha}{os.path.sep}coverage.json
        """

        p = Popen(run_tacoco_reader_cmd, cwd=self.tacoco_path, shell=True)

        return p.wait()
