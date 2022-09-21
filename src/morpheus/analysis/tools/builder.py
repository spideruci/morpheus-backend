from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import logging
import os
from morpheus.analysis.util.subject import AnalysisRepo

logger = logging.getLogger(__name__)


class ProjectBuilder(ABC):
    @abstractmethod
    def __init__(self, repo: AnalysisRepo, log_path=subprocess.DEVNULL):
        self._repo = repo
        self._builder_log = log_path

    @abstractmethod
    def clean(self) -> ProjectBuilder:
        pass

    @abstractmethod
    def compile(self) -> ProjectBuilder:
        pass

    @abstractmethod
    def test_compile(self) -> ProjectBuilder:
        pass

    @staticmethod
    def get_builder(repo: AnalysisRepo) -> ProjectBuilder:
        project_path: Path = Path(repo.get_project_directory())
        
        if (project_path / "mvnw").exists():
            return MavenBuilder(repo)
        elif (project_path / "pom.xml").exists():
            return MavenBuilder(repo, wrapper=False)
        elif (project_path / "gradlew").exists():
            return GradleBuilder(repo)
        elif (project_path / "build.gradle").exists():
            return GradleBuilder(repo, wrapper=False)
        
        raise RuntimeError("Project Builder not found.")

    def set_log_path(self, log_path) -> ProjectBuilder:
        self.builder_log = log_path
        return self

    def run_command(self, cmd) -> None:
        my_env = os.environ.copy()

        logger.debug("[ProjectBuilder] command run: %s", cmd)
        result = subprocess.run(cmd, stdout=self.builder_log, stderr=self.builder_log, env=my_env, shell=True, cwd=self._repo.get_project_directory())

        if result.returncode != 0:
            raise RuntimeError(f"Command failed to run: {cmd}")


class MavenBuilder(ProjectBuilder):
    MVN_CMD = "./mvnw"
    MVN_ARGS = "--fail-fast"

    def __init__(self, repo: AnalysisRepo, log_path=subprocess.DEVNULL, wrapper: bool=True):
        super().__init__(repo, log_path)
        if not wrapper:
            self.MVN_CMD = "mvn"
    
    def clean(self) -> ProjectBuilder:
        logger.info("[MAVEN] Phase: clean: %s", self._repo.get_project_directory())
        cmd = [f"{self.MVN_CMD} {self.MVN_ARGS} clean"]

        self.run_command(cmd)

        return self
    
    def compile(self) -> ProjectBuilder:
        logger.info("[MAVEN] Phase: compile: %s", self._repo.get_project_directory())
        cmd = [f"{self.MVN_CMD} {self.MVN_ARGS} compile"]

        self.run_command(cmd)

        return self

    def test_compile(self) -> ProjectBuilder:
        logger.info("[MAVEN] Phase: test compile: %s", self._repo.get_project_directory())
        cmd = [f"{self.MVN_CMD} test-compile"]

        self.run_command(cmd)

        return self


class GradleBuilder(ProjectBuilder):
    GRADLE_CMD = "./gradlew"

    def __init__(self, repo: AnalysisRepo, log_path=subprocess.DEVNULL, wrapper=True):
        super().__init__(repo, log_path)
        if not wrapper:
            self.GRADLE_CMD = "gradle"

    def clean(self) -> ProjectBuilder:
        logger.info("[GRADLE] Phase: clean: %s", self._repo.get_project_directory())
        cmd = [f"{self.GRADLE_CMD} clean"]

        self.run_command(cmd)

        return self

    def compile(self) -> ProjectBuilder:
        logger.info("[GRADLE] Phase: classes: %s", self._repo.get_project_directory())
        cmd = [f"{self.GRADLE_CMD} classes"]

        self.run_command(cmd)

        return self

    def test_compile(self) -> ProjectBuilder:
        logger.info("[GRADLE] phase: testClasses: %s", self._repo.get_project_directory())
        cmd = [f"{self.GRADLE_CMD} testClasses"]

        self.run_command(cmd)

        return self
