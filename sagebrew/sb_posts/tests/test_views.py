import time
from json import dumps, loads
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


from plebs.neo_models import Pleb
from sb_posts.views import save_post_view, edit_post, delete_post
class SubmitPostTest(TestCase):

    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
            username='Tyler', email='tyler.wiersing@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
            username='Tyler', email='tyler.wiersing@gmail.com')


    def test_submit_post_without_profane_content(self):
        my_dict = {"content": "This is a clean post",
                   "current_pleb": self.user.email,
                   "wall_pleb": self.user.email}
        request = self.factory.post('/posts/submit_post/', data=my_dict)
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 200)
        time.sleep(1)

    def test_submit_post_with_profane_content(self):
        my_dict = {"content": "Fuck Shit Dicks Cock Niggers Spic Ass Cunt Fag",
                   "current_pleb": "tyler.wiersing@gmail.com",
                   "wall_pleb": "tyler.wiersing@gmail.com"}
        request = self.factory.post('/posts/submit_post/', data=my_dict)
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 200)
        time.sleep(1)

class PostRaceConditionTests(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
            username='Tyler', email='tyler.wiersing@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
            username='Tyler', email='tyler.wiersing@gmail.com')

    def test_race_condition_create_post_edit_post(self):
        my_dict = {"content":"Testing race condition pre edit",
                    "current_pleb": self.user.email,
                    "wall_pleb": self.user.email}
        request1 = self.factory.post('/posts/submit_post/', data=my_dict, format='json')
        request1.user = self.user
        response1 = save_post_view(request1)
        response_data = response1.data
        print response_data
        response_data['filtered_content'].pop('content', None)
        response_data['filtered_content'].pop('current_pleb',None)
        response_data['filtered_content'].pop('wall_pleb',None)
        response_data['filtered_content']['content'] = 'Post Edit'
        response_data_dict = response_data['filtered_content'].dict()
        request2 = self.factory.post('/posts/edit_post/', data=response_data_dict, format='json')
        request2.user = self.user
        response2 = edit_post(request2)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        time.sleep(1)

    def test_race_condition_create_delete(self):
        my_dict = {"content":"Testing race condition delete",
                   "current_pleb": self.user.email,
                   "wall_pleb": self.user.email}
        request1 = self.factory.post('/posts/submit_post/', data=my_dict)
        request1.user = self.user
        response1 = save_post_view(request1)
        response_data = response1.data
        response_data_dict = response_data['filtered_content'].dict()
        response_data_dict.pop('content', None)
        response_data_dict.pop('wall_pleb', None)
        response_data_dict.pop('current_pleb', None)
        request2 = self.factory.post('/posts/delete_post/', data=response_data_dict)
        request2.user = self.user
        response2 = delete_post(request2)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        time.sleep(1)

    def test_race_condition_edit_twice(self):
        my_dict = {"content":"Testing race condition pre edit",
                    "current_pleb": self.user.email,
                    "wall_pleb": self.user.email}
        request1 = self.factory.post('/posts/submit_post/', data=my_dict)
        request1.user = self.user
        response1 = save_post_view(request1)
        response_data = response1.data
        response_data['filtered_content'].pop('content', None)
        response_data['filtered_content'].pop('current_pleb',None)
        response_data['filtered_content'].pop('wall_pleb',None)
        response_data['filtered_content']['content'] = 'Post Edit 1'
        response_data_dict = response_data['filtered_content'].dict()
        request2 = self.factory.post('/posts/edit_post/', data=response_data_dict)
        request2.user = self.user
        response2 = edit_post(request2)
        response_data_dict['content'] = 'Post Edit 2'
        request3 = self.factory.post('/posts/edit_post/', data=response_data_dict)
        request3.user = self.user
        response3 = edit_post(request3)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        time.sleep(1)

    def test_race_condition_delete_twice(self):
        my_dict = {"content":"Testing race condition delete",
                   "current_pleb": self.user.email,
                   "wall_pleb": self.user.email}
        request1 = self.factory.post('/posts/submit_post/', data=my_dict)
        request1.user = self.user
        response1 = save_post_view(request1)
        response_data = response1.data
        response_data_dict = response_data['filtered_content'].dict()
        response_data_dict.pop('content', None)
        response_data_dict.pop('wall_pleb', None)
        response_data_dict.pop('current_pleb', None)
        request2 = self.factory.post('/posts/delete_post/', data=response_data_dict)
        request2.user = self.user
        response2 = delete_post(request2)
        request3 = self.factory.post('/posts/delete_post/', data=response_data_dict)
        request3.user = self.user
        response3 = delete_post(request3)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        time.sleep(1)


