from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse as dj_reverse
from django.utils.text import slugify

from rest_framework.reverse import reverse

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
                href = reverse('post-detail',
                               kwargs={'object_uuid': post.object_uuid})
                post.url = dj_reverse('profile_page', kwargs={
                    'pleb_username': post.get_wall_owner_profile().username
                })
                if 'https://' not in href:
                    post.href = "%s%s" % (settings.WEB_ADDRESS, href)
                else:
                    post.href = href
                post.save()
            for comment in Comment.nodes.all():
                parent_object = get_parent_object(comment.object_uuid)
                if parent_object is not None:
                    req_url = reverse(
                        '%s-detail' % parent_object.get_child_label().lower(),
                        kwargs={
                            'object_uuid': parent_object.object_uuid
                        })
                    if 'https://' not in req_url:
                        parent_url = "%s%s" % (settings.WEB_ADDRESS, req_url)
                    else:
                        parent_url = req_url
                    response = request_to_api(
                        parent_url, comment.owner_username, req_method="GET")
                    try:
                        comment.url = response.json()['url']
                    except ValueError:
                        pass
                href = reverse("comment-detail",
                               kwargs={'object_uuid': comment.object_uuid})
                if 'https://' not in href:
                    comment.href = "%s%s" % (settings.WEB_ADDRESS, href)
                else:
                    comment.href = href
                comment.save()
            for question in Question.nodes.all():
                url = dj_reverse('question_detail_page',
                                 kwargs={'question_uuid': question.object_uuid,
                                         'slug': slugify(question.title)})
                href = reverse('question-detail',
                               kwargs={'object_uuid': question.object_uuid})
                question.url = url
                if 'https://' not in href:
                    question.href = "%s%s" % (settings.WEB_ADDRESS, href)
                else:
                    question.href = href
                question.save()
            for solution in Solution.nodes.all():
                url = solution.get_url()
                if 'https://' not in url:
                    solution.url = "%s%s" % (settings.WEB_ADDRESS, url)
                else:
                    solution.url = url

                href = reverse('solution-detail',
                               kwargs={"object_uuid": solution.object_uuid})
                if 'https://' not in href:
                    solution.href = "%s%s" % (settings.WEB_ADDRESS, href)
                else:
                    solution.href = href
                solution.save()
            return
        except Exception:
            pass

    def handle(self, *args, **options):
        self.add_url_and_href()
