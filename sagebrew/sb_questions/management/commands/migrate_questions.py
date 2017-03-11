from django.core.management.base import BaseCommand

from neomodel import db

from sagebrew.api.utils import spawn_task
from sagebrew.sb_questions.neo_models import Question
from sagebrew.sb_questions.tasks import create_question_summary_task


class Command(BaseCommand):
    args = 'None.'

    def migrate_questions(self):
        query = 'MATCH (a:Question) RETURN a'

        res, _ = db.cypher_query(query)
        for question in [Question.inflate(row[0]) for row in res]:
            spawn_task(task_func=create_question_summary_task, task_param={
                'object_uuid': question.object_uuid
            })
        self.stdout.write("completed question migration\n", ending='')

    def handle(self, *args, **options):
        self.migrate_questions()
