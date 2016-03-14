from django.core.management.base import BaseCommand

from neomodel import db

from api.utils import spawn_task

from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_solutions.tasks import create_solution_summary_task


class Command(BaseCommand):
    args = 'None.'

    def migrate_solutions(self):
        for solution in Solution.nodes.all():
            query = "MATCH (a:Solution {object_uuid:'%s'})" \
                    "-[:POSSIBLE_ANSWER]->" \
                    "(b:Question) RETURN b" % solution.object_uuid
            res, col = db.cypher_query(query)
            parent = Question.inflate(res.one)
            solution.parent_id = parent.object_uuid
            solution.save()
            spawn_task(task_func=create_solution_summary_task, task_param={
                'object_uuid': solution.object_uuid
            })

    def handle(self, *args, **options):
        self.migrate_solutions()
