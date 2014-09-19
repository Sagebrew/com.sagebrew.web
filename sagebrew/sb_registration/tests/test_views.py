from uuid import uuid1

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.core.management import call_command

from sb_registration.views import profile_information


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


class ProfileInfoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_user_info_population_no_birthday(self):
        my_dict = {'date_of_birth': [u'']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_user_info_population_incorrect_birthday(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_zipcode(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_primary(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u''],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertEqual(response.status_code, 200)

    def test_address_validation_util_invalid_no_country(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u''], u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertEqual(response.status_code, 200)

    def test_address_validation_util_invalid_no_city(self):
        my_dict = {u'city': [u''], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertEqual(response.status_code, 200)

    def test_address_validation_util_valid(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])



