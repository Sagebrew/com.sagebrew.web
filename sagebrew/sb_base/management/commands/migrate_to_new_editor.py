from django.core.management.base import BaseCommand

from neomodel import db

from api.utils import render_content
from sb_questions.neo_models import Question
from sb_missions.neo_models import Mission
from sb_solutions.neo_models import Solution
from sb_updates.neo_models import Update


class Command(BaseCommand):
    args = 'None.'

    def clear_neo_db(self):
        skip = 0
        while True:
            query ='MATCH (m:Mission) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for mission in [Mission.inflate(row[0]) for row in res]:
                rendered = render_content(mission.epic, mission.object_uuid)
                mission.epic = rendered
                mission.temp_epic = rendered
                mission.save()
        skip = 0
        while True:
            query ='MATCH (m:Question) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for question in [Question.inflate(row[0]) for row in res]:
                rendered = render_content(question.content,
                                          question.object_uuid)
                question.content = rendered
                question.save()
        skip = 0
        while True:
            query ='MATCH (m:Solution) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for solution in [Solution.inflate(row[0]) for row in res]:
                rendered = render_content(solution.content,
                                          solution.object_uuid)
                solution.content = rendered
                solution.save()
        skip = 0
        while True:
            query ='MATCH (m:Update) RETURN m SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for update in [Update.inflate(row[0]) for row in res]:
                rendered = render_content(update.content, update.object_uuid)
                update.content = rendered
                update.save()


    def handle(self, *args, **options):
        self.clear_neo_db()
