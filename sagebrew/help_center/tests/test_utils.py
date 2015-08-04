from django.test import TestCase

from help_center.utils import populate_urls


class TestPopulateURLs(TestCase):
    def test_populate_urls(self):
        res = populate_urls()

        self.assertIsInstance(res, list)
