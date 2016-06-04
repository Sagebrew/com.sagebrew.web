from django.core.cache import cache
from django.core.management.base import BaseCommand

from neomodel import db

from api.utils import render_content
from sb_questions.neo_models import Question
from sb_missions.neo_models import Mission
from sb_solutions.neo_models import Solution
from sb_updates.neo_models import Update


class Command(BaseCommand):
    args = 'None.'

    def migrate_to_new_editor(self):
        skip = 0
        while True:
            query = 'MATCH (m:Mission) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for mission in [Mission.inflate(row[0]) for row in res]:
                rendered = render_content(mission.epic)
                mission.epic = rendered
                mission.temp_epic = rendered
                mission.save()
        skip = 0
        while True:
            query = 'MATCH (m:Question) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for question in [Question.inflate(row[0]) for row in res]:
                rendered = render_content(question.content)
                question.content = rendered
                question.save()
        skip = 0
        while True:
            query = 'MATCH (m:Solution) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for solution in [Solution.inflate(row[0]) for row in res]:
                rendered = render_content(solution.content)
                solution.content = rendered
                solution.save()
        skip = 0
        while True:
            query = 'MATCH (m:Update) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for update in [Update.inflate(row[0]) for row in res]:
                rendered = render_content(update.content)
                update.content = rendered
                update.save()
        cache.set("migrated_to_new_editor", True)

    def handle(self, *args, **options):
        test_migrated = cache.get("migrated_to_new_editor")
        if not test_migrated:
            self.migrate_to_new_editor()
        print("Migration to new editor successful")
