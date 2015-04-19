from django.test import TestCase

from api.utils import (add_failure_to_queue)


class TestAddFailureToQueue(TestCase):
    def setUp(self):
        self.message = {
            'message': 'this is a test message to add if a task fails'
        }

    def test_adding_failure_to_queue(self):
        self.assertTrue(add_failure_to_queue(self.message))
