from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from sb_posts.views import save_post_view, get_user_posts
class SubmitPostTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email='tyler.wiersing@gmail.com')


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

    def test_get_user_posts(self):
        pass