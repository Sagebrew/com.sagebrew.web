from logging import getLogger

from django.core.management.base import BaseCommand

from neomodel import db

from sb_search.tasks import update_search_object

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def repopulate_elasticsearch(self):
        query = 'MATCH (quests:Quest), (plebs:Pleb), ' \
                '(missions:Mission), (questions:Question) ' \
                'RETURN collect(DISTINCT quests.object_uuid) as quests, ' \
                'collect(DISTINCT plebs.object_uuid) as plebs, ' \
                'collect(DISTINCT missions.object_uuid) as missions, ' \
                'collect(DISTINCT questions.object_uuid) as questions '
        res, _ = db.cypher_query(query)
        for row in res:
            if row.quests is not None:
                for quest in row.quests:
                    update_search_object.apply_async(
                        kwargs={"object_uuid": quest, "label": "quest"})
            if row.plebs is not None:
                for pleb in row.plebs:
                    update_search_object.apply_async(
                        kwargs={"object_uuid": pleb, "label": "pleb"})
            if row.missions is not None:
                for mission in row.missions:
                    update_search_object.apply_async(
                        kwargs={"object_uuid": mission, "label": 'mission'})
            if row.questions is not None:
                for question in row.questions:
                    update_search_object.apply_async(
                        kwargs={'object_uuid': question, 'label': 'question'})

    def handle(self, *args, **options):
        self.repopulate_elasticsearch()
        logger.info("Completed elasticsearch repopulation")
