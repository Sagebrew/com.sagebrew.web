from django.contrib.auth.models import User
from django.test import TestCase


class InterestsTest(TestCase):

    def setup(self):
        self.user = User.objects.get(pk=2)

    def test_no_categories_no_topics_selected(self):
        pass

    def test_all_categories_no_topics_selected(self):
        pass

    def test_all_topics_no_cat_selected(self):
        pass

    def test_all_categories_all_topics_selected(self):
        pass

    def test_random_cat_selected_no_topics_selected(self):
        pass

    def test_random_cat_selected_random_topics_selected(self):
        pass

    def test_no_cat_selected_random_topics_selected(self):
        pass

    def test_get_request(self):
        pass