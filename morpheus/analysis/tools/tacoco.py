"""
Script for running tacoco on a project
"""
import os
import logging
import subprocess
from pathlib import Path
from typing import List
from morpheus.analysis.util.subject import AnalysisRepo
from morpheus.database.models.repository import Commit

logger = logging.getLogger(__name__)

class TacocoRunner():

    def __init__(self, repo: AnalysisRepo, output_dir: Path, tacoco_path: str, jdk: str = "13"):
        self.__repo = repo
        self.project_path = repo.get_project_directory()
        self.tacoco_path = tacoco_path
        self.project_name = self.__repo.get_project_name()
        self.file_output_dir = output_dir / self.project_name

    def install(self):
        logger.info("[TACOCO] Phase: install on: %s", self.project_path)

        cmd = [f"mvn install"]
        ret = self.__run_command(cmd)

        if ret == 1:
            raise Exception("'mvn install' failed...")

        return self

    def __get_logfile(self, commit):
        log_path =  (self.file_output_dir / self.__repo.get_current_commit().sha / "tacoco_run.log").resolve()

        os.makedirs((self.file_output_dir / self.__repo.get_current_commit().sha).resolve(), exist_ok=True)
        return open(log_path, "a")

    def compile(self):
        logger.info("[TACOCO] Phase: compile: %s", self.project_path)

        cmd = ["mvn compile"]

        ret = self.__run_command(cmd)

        if ret == 1:
            logger.warn("Comipile with java 1.8...")
            cmd = ["mvn compile -Dmaven.compiler.target=1.8 -Dmaven.compiler.source=1.8"]
            ret = self.__run_command(cmd)

        if ret == 1:
            logger.error("RET %s", ret)
            raise Exception("'mvn compile' failed...")

        return self

    def test_compile(self):
        logger.info("[TACOCO] Phase: test compile: %s", self.project_path)

        cmd = [f"mvn test-compile"]

        ret = self.__run_command(cmd)

        if ret == 1:
            logger.warn("compile with java 1.8...")
            cmd = ["mvn test-compile -Dmaven.compiler.target=1.8 -Dmaven.compiler.source=1.8"]
            ret = self.__run_command(cmd)

        if ret == 1:
            logger.error("RET test-compile %s", ret)
            raise Exception("'mvn test-compile' failed...")

        return self

    def __run_command(self, cmd):
        commit = self.__repo.get_current_commit()

        # Store all logs per project per commit
        with self.__get_logfile(commit.sha) as log_file:
            # If tacoco was already run before it places a classpath in the root directory
            # which causes problems for a rerun for some checks (apache-rat-plugin).
            rm_tacoco_cp_cmd: List[str] = ["rm", "tacoco.cp"]

            my_env = os.environ.copy()
            # subprocess.run(rm_tacoco_cp_cmd, shell=True, cwd=self.project_path)

            logger.debug("[TACOCO] command run: %s", cmd)
            result = subprocess.run(cmd, stdout=log_file, stderr=log_file, env=my_env, shell=True, cwd=self.project_path)

        return result.returncode

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
        with self.__get_logfile(commit.sha) as log_file:
            result = subprocess.run(run_tacoco_coverage_cmd, cwd=self.tacoco_path, stderr=log_file, stdout=log_file, shell=True)
        return result.returncode

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
        with self.__get_logfile(commit.sha) as log_file:
            result = subprocess.run(run_tacoco_analysis_cmd, cwd=self.tacoco_path, stderr=log_file, stdout=log_file, shell=True)
        return result.returncode

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
        with self.__get_logfile(commit.sha) as log_file:
            result = subprocess.run(run_tacoco_reader_cmd, cwd=self.tacoco_path, stderr=log_file, stdout=log_file, shell=True)
        return result.returncode
