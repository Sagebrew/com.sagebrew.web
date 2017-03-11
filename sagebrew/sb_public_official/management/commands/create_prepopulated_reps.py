from logging import getLogger
from localflavor.us.us_states import US_STATES

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import cache

from neo4j.v1 import CypherError
from neomodel import DoesNotExist, db

from sagebrew.api.utils import spawn_task
from sagebrew.govtrack.neo_models import GTRole, GTPerson
from sagebrew.govtrack.utils import populate_term_data
from sagebrew.sb_search.tasks import update_search_object

from sagebrew.sb_public_official.neo_models import PublicOfficial
from sagebrew.sb_quests.neo_models import Quest

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    help = 'Creates placeholder representatives.'

    def create_prepopulated_reps(self):
        count = 0
        while True:
            query = 'MATCH (role:GTRole) ' \
                    'RETURN role SKIP %s LIMIT 25' % count
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            count += 24
            for role in [GTRole.inflate(row[0]) for row in res]:
                if role.current:
                    query = 'MATCH (role:GTRole {role_id: %s})' \
                            '-[:IS]->(person:GTPerson) ' \
                            'RETURN person' % role.role_id
                    res, _ = db.cypher_query(query)
                    if res.one is None:
                        continue
                    else:
                        person = GTPerson.inflate(res.one)

                    try:
                        rep = PublicOfficial.nodes.get(gt_id=person.gt_id)
                    except(DoesNotExist, PublicOfficial.DoesNotExist):
                        try:
                            state = dict(US_STATES)[role.state]
                        except KeyError:
                            state = role.state
                        rep = PublicOfficial(
                            first_name=person.firstname,
                            last_name=person.lastname,
                            gender=person.gender, date_of_birth=person.birthday,
                            name_mod=person.namemod, current=role.current,
                            bio=role.description, district=role.district,
                            state=state, title=role.title,
                            website=role.website, start_date=role.startdate,
                            end_date=role.enddate, full_name=person.name,
                            twitter=person.twitterid, youtube=person.youtubeid,
                            gt_id=person.gt_id, gov_phone=role.phone,
                            bioguideid=person.bioguideid)
                        rep.save()
                    except (CypherError, IOError) as e:
                        logger.exception(e)
                        continue
                    quest = rep.get_quest()
                    if not quest:
                        quest = Quest(
                            about=rep.bio, youtube=rep.youtube,
                            twitter=rep.twitter, website=rep.website,
                            first_name=rep.first_name, last_name=rep.last_name,
                            owner_username=rep.object_uuid,
                            title="%s %s" % (rep.first_name, rep.last_name),
                            profile_pic="%s/representative_images/225x275/"
                                        "%s.jpg" % (
                                            settings.LONG_TERM_STATIC_DOMAIN,
                                            rep.bioguideid)).save()
                        rep.quest.connect(quest)
                    else:
                        quest.profile_pic = \
                            "%s/representative_images/225x275/" \
                            "%s.jpg" % (settings.LONG_TERM_STATIC_DOMAIN,
                                        rep.bioguideid)
                        quest.save()
                        cache.set('%s_quest' % quest.object_uuid, quest)
                    rep.gt_person.connect(person)
                    rep.gt_role.connect(role)
                    task_data = {
                        "object_uuid": quest.object_uuid,
                        "label": 'quest',
                    }
                    spawn_task(update_search_object, task_data)
        populate_term_data()

    def handle(self, *args, **options):
        self.create_prepopulated_reps()
