from django.core.management.base import BaseCommand

from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution


class Command(BaseCommand):
    args = 'None.'

    def add_url_and_href(self):
        for post in Post.nodes.all():
            pass
        for comment in Comment.nodes.all():
            pass
        for question in Question.nodes.all():
            pass
        for solution in Solution.nodes.all():
            pass
        return

    def handle(self, *args, **options):
        self.add_url_and_href()
