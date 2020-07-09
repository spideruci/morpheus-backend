"""
Script for running history slicing (method granularity) on a project
"""
#!/bin/python3
import argparse
import subprocess
import os

from pathlib import Path
from subprocess import Popen, PIPE, call, check_output

from spidertools.utils.git_repo import GitRepo


class HistoryRunner():

    def __init__(self, repo: GitRepo, output_dir: str, history_slicer_path: str):
        self.__repo = repo
        self.project_path = repo.get_project_directory()
        self.history_slicer_path = history_slicer_path
        self.project_name = self.__repo.get_project_name()
        self.file_output_dir = output_dir + os.path.sep + self.project_name

    def run(self):
        print(f"[HISTORY SLICER] start analysis... {self.project_path}")

        run_history_analysis_cmd = f"""
        ./gradlew experiment:run --args="--sut {self.project_path} --output {self.file_output_dir}{os.path.sep}history.json"
        """

        p = Popen(run_history_analysis_cmd, cwd=self.history_slicer_path, shell=True)
        return p.wait()

class MethodParserRunner():

    def __init__(self, repo: GitRepo, output_dir: str, history_slicer_path: str):
        self.__repo = repo
        self.project_path = repo.get_project_directory()
        self.history_slicer_path = history_slicer_path
        self.project_name = self.__repo.get_project_name()
        self.file_output_dir = output_dir + os.path.sep + self.project_name

    def run(self):
        print(f"[Method Parser] start analysis... {self.project_path}")

        run_method_parser_cmd = f"""
        ./gradlew method-parser:run --args="--sut {self.project_path} --outputPath {self.file_output_dir}{os.path.sep}methods-{self.__repo.get_current_commit()}.json"
        """

        p = Popen(run_method_parser_cmd, cwd=self.history_slicer_path, shell=True)
        return p.wait()