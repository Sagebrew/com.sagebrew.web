from django.core.management.base import BaseCommand

from neomodel import db

from sagebrew.sb_quests.neo_models import Quest
from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_donations.neo_models import Donation


class Command(BaseCommand):

    def convert_donations(self):
        skip = 0
        while True:
            query = 'MATCH (quest:Quest) RETURN quest ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res[0] if res else None:
                break
            for quest in [Quest.inflate(row[0]) for row in res]:
                mission_query = 'MATCH (a:Quest {owner_username: "%s"})' \
                                '-[:EMBARKS_ON]->(m:Mission) RETURN m' \
                                % quest.owner_username
                mission_res, _ = db.cypher_query(mission_query)
                try:
                    mission = Mission.inflate(mission_res[0][0])
                except IndexError:
                    continue
                donation_query = 'MATCH (a:Quest {owner_username: "%s"})' \
                                 '<-[:CONTRIBUTED_TO]-(b:Donation) ' \
                                 'RETURN b' % quest.owner_username
                donation_res, _ = db.cypher_query(donation_query)
                for donation in [Donation.inflate(donation_row[0])
                                 for donation_row in donation_res]:
                    try:
                        if not Donation.get_mission(donation.object_uuid):
                            donation.mission.connect(mission)
                    except Exception:
                        pass
        self.stdout.write("completed donation migration\n", ending='')

        return True

    def handle(self, *args, **options):
        self.convert_donations()
