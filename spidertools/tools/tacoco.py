"""
Script for running tacoco on a project
"""
#!/bin/python3
import argparse
import subprocess
import os

from pathlib import Path
from subprocess import Popen, PIPE, call, check_output

from spidertools.utils.git_repo import GitRepo


class TacocoRunner():

    def __init__(self, repo: GitRepo, output_dir: str, tacoco_path: str, jdk: str = "13"):
        self.__repo = repo
        self.project_path = repo.get_project_directory()
        self.tacoco_path = tacoco_path
        self.project_name = self.__repo.get_project_name()
        self.file_output_dir = output_dir + os.path.sep + self.project_name

    def build(self):
        print(f"[TACOCO] start builder... {self.project_path}")

        # If tacoco was already run before it places a classpath in the root directory
        # which causes problems for a rerun for some checks (apache-rat-plugin).
        p = Popen(["rm", "tacoco.cp"], cwd=self.project_path)
        p.wait()
        # TODO Make use of the tacoco build capabilities...
        p = Popen([f"mvn compile test-compile -Dmaven.compiler.source=11 -Dmaven.compiler.target=11 -Danimal.sniffer.skip=True"], cwd=self.project_path, shell=True)
        return p.wait()

    def run(self):
        self.__run_tacoco_coverage()
        self.__run_tacoco_analysis()
        self.__run_tacoco_reader()

    def __run_tacoco_coverage(self):
        print(f"[TACOCO] start coverage... {self.project_path}")

        run_tacoco_coverage_cmd = f"""
        mvn exec:java \
            -Plauncher \
            -Dtacoco.sut={self.project_path} \
            -Dtacoco.home={self.tacoco_path} \
            -Dtacoco.project={self.__repo.get_current_commit()} \
            -Dtacoco.outdir={self.file_output_dir} \
            -Danalyzer.opts="configs/tacoco-analyzer.config"
        """

        p = Popen(run_tacoco_coverage_cmd, cwd=self.tacoco_path, shell=True)
        return p.wait()

    def __run_tacoco_analysis(self):
        print(f"[TACOCO] start analysis... {self.project_path}")

        run_tacoco_analysis_cmd = f"""
        mvn exec:java \
            -Panalyzer \
            -Dtacoco.sut={self.project_path} \
            -Dtacoco.exec={self.file_output_dir}{os.path.sep}{self.__repo.get_current_commit()}.exec \
            -Dtacoco.json={self.file_output_dir}{os.path.sep}{self.__repo.get_current_commit()}.json
        """

        p = Popen(run_tacoco_analysis_cmd, cwd=self.tacoco_path, shell=True)
        return p.wait()

    def __run_tacoco_reader(self):
        print(f"[TACOCO] start reader... {self.project_path}")

        run_tacoco_reader_cmd = f"""
        mvn exec:java \
            -Preader \
            -Dtacoco.json={self.file_output_dir}{os.path.sep}{self.__repo.get_current_commit()}.json
        """

        p = Popen(run_tacoco_reader_cmd, cwd=self.tacoco_path, shell=True)

        return p.wait()
