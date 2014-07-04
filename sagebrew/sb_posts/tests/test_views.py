from json import dumps
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


from plebs.neo_models import Pleb
from sb_posts.views import save_post_view, edit_post
class SubmitPostTest(TestCase):

    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email='tyler.wiersing@gmail.com')

    def tearDown(self):
        pleb = Pleb.index.get(email=self.user.email)
        pleb.delete()


    def test_submit_post_with_profane_content(self):
        my_dict = {"content": "Fuck Shit Dicks Cock Niggers Spic Ass Cunt Fag",
                   "pleb": "tyler.wiersing@gmail.com"}
        request = self.factory.post('/posts/submit_post/', data=my_dict)
        request.user = self.user
        response = save_post_view(request)
        self.assertEqual(response.status_code, 200)

    def test_submit_post_without_profane_content(self):
        my_dict = {"content": "This is a clean post",
                   "pleb": "tyler.wiersing@gmail.com"}
        request = self.factory.post('/posts/submit_post/', data=my_dict)
        request.user = self.user
        response = save_post_view(request)
        self.assertEqual(response.status_code, 200)

    def test_race_condition_create_post_edit_post(self):
        my_dict = {"content":"Testing race condition pre edit",
                    "pleb": "tyler.wiersing@gmail.com",}
        request1 = self.factory.post('/posts/submit_post/', data=my_dict)
        request1.user = self.user
        response1 = save_post_view(request1)
        response_data = dumps(response1.data)
        print response_data
        request2 = self.factory.post('/posts/edit_post/', data=response_data)
        request2.user = self.user
        response2 = edit_post(request2)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
