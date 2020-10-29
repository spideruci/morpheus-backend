import unittest
from spidertools.storage.data.selectors import filter_selector
from spidertools.storage.data.filtering import no_filter

class TestFilter(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter_selection(self):
        result = filter_selector(no_filter.__name__)
        assert result == no_filter
