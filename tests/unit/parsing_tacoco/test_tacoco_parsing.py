import unittest
from pathlib import Path
from morpheus.analysis.parser.tacoco import TacocoParser
from morpheus.commands.db import load_json


class TacocoParsingTest(unittest.TestCase):

    def test_parsing_jpacman(self):
        tacoco_file = Path('./tests/resources/jpacman-coverage-cov-matrix.json')
        tacoco_coverage = load_json(tacoco_file)

        coverage = TacocoParser() \
            .parse(tacoco_coverage)

        assert len(coverage) == 45 # One less because of 'end' method
