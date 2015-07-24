from logging import getLogger

from django.core.management.base import BaseCommand

from sb_posts.neo_models import Post

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates privilege, requirement, action and restrictions.'

    def update_posts(self):
        posts = Post.nodes.all()
        for post in posts:
            post.wall_owner_username = post.get_wall_owner_profile().username
            post.save()

    def handle(self, *args, **options):
        self.update_posts()
        logger.critical("Updated posts")
