from django.core.management.base import BaseCommand

from neomodel import db

from api.utils import spawn_task

from sb_solutions.neo_models import Solution
from sb_solutions.tasks import create_solution_summary_task


class Command(BaseCommand):
    args = 'None.'

    def migrate_solutions(self):
        query = 'MATCH (a:Solution)<-[:POSSIBLE_ANSWER]-(b:Question) ' \
                'SET a.parent_id=b.object_uuid RETURN a'
        res, _ = db.cypher_query(query)
        for solution in [Solution.inflate(row[0]) for row in res]:
            spawn_task(task_func=create_solution_summary_task, task_param={
                'object_uuid': solution.object_uuid
            })
        self.stdout.write("completed solution migration\n", ending='')

    def handle(self, *args, **options):
        self.migrate_solutions()
