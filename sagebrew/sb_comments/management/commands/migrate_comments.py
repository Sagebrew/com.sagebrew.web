from django.core.management.base import BaseCommand

from neomodel import db

from sb_base.neo_models import SBContent
from sb_comments.neo_models import Comment


class Command(BaseCommand):
    args = 'None.'

    def migrate_comments(self):
        for comment in Comment.nodes.all():
            query = "MATCH (a:Comment {object_uuid:'%s'})<-[:HAS_A]-" \
                    "(b:SBContent) RETURN b" % comment.object_uuid
            res, _ = db.cypher_query(query)
            parent = SBContent.inflate(res.one)
            comment.parent_id = parent.object_uuid
            comment.save()

    def handle(self, *args, **options):
        self.migrate_comments()
