from django.conf import settings
from django.core.management.base import BaseCommand

from rest_framework.reverse import reverse

from neomodel import DoesNotExist

from api.utils import request_to_api
from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_comments.serializers import get_parent_object


class Command(BaseCommand):
    args = 'None.'

    def add_url_and_href(self):
        try:
            for post in Post.nodes.all():
                try:
                    url = post.get_url()
                except DoesNotExist:
                    url = ""
                href = reverse('post-detail',
                               kwargs={'object_uuid': post.object_uuid})
                post.url = "%s%s" % (settings.WEB_ADDRESS, url)
                post.href = "%s%s" % (settings.WEB_ADDRESS, href)
                post.save()
            for comment in Comment.nodes.all():
                parent_object = get_parent_object(comment.object_uuid)
                if parent_object is not None:
                    req_url = reverse(
                        '%s-detail' % parent_object.get_child_label().lower(),
                        kwargs={
                            'object_uuid': parent_object.object_uuid
                        })
                    parent_url = "%s%s" % (settings.WEB_ADDRESS, req_url)
                    response = request_to_api(parent_url, comment.owner_username,
                                              req_method="GET")
                    try:
                        url = response.json()['url']
                        comment.url = "%s%s" % (settings.WEB_ADDRESS, url)
                    except ValueError:
                        pass
                href = reverse("comment-detail",
                               kwargs={'object_uuid': comment.object_uuid})
                comment.href = "%s%s" % (settings.WEB_ADDRESS, href)
                comment.save()
            for question in Question.nodes.all():
                url = question.get_url()
                href = reverse('question-detail',
                               kwargs={'object_uuid': question.object_uuid})
                question.url = "%s%s" % (settings.WEB_ADDRESS, url)
                question.href = "%s%s" % (settings.WEB_ADDRESS, href)
                question.save()
            for solution in Solution.nodes.all():
                url = solution.get_url()
                href = reverse('solution-detail',
                               kwargs={"object_uuid": solution.object_uuid})
                solution.url = "%s%s" % (settings.WEB_ADDRESS, url)
                solution.href = "%s%s" % (settings.WEB_ADDRESS, href)
                solution.save()
            return
        except Exception:
            pass

    def handle(self, *args, **options):
        self.add_url_and_href()
