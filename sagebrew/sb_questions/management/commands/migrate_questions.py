from django.core.management.base import BaseCommand

from api.utils import spawn_task
from sb_questions.neo_models import Question
from sb_questions.tasks import create_question_summary_task


class Command(BaseCommand):
    args = 'None.'

    def migrate_questions(self):
        for question in Question.nodes.all():
            spawn_task(task_func=create_question_summary_task, task_param={
                'object_uuid': question.object_uuid
            })

    def handle(self, *args, **options):
        self.migrate_questions()
