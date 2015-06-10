from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from govtrack.neo_models import GTRole
from govtrack.utils import populate_term_data
from sb_campaigns.neo_models import PoliticalCampaign

from sb_public_official.neo_models import PublicOfficial
from sb_public_official.serializers import PublicOfficialSerializer

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def create_placeholders(self):
        reps = []
        try:
            roles = GTRole.nodes.all()
        except (IOError, CypherException):
            return False
        for role in roles:
            if role.current:
                try:
                    person = role.person.all()[0]
                except IndexError:
                    continue
                except (CypherException, IOError) as e:
                    logger.exception(e)
                    continue
                try:
                    rep = PublicOfficial.nodes.get(gt_id=person.gt_id)
                except(DoesNotExist, PublicOfficial.DoesNotExist):
                    rep = PublicOfficial(first_name=person.firstname,
                                         last_name=person.lastname,
                                         gender=person.gender,
                                         date_of_birth=person.birthday,
                                         namemod=person.namemod,
                                         current=role.current,
                                         bio=role.description,
                                         district=role.district,
                                         state=role.state,
                                         title=role.title,
                                         website=role.website,
                                         start_date=role.startdate,
                                         end_date=role.enddate,
                                         full_name=person.name,
                                         twitter=person.twitterid,
                                         youtube=person.youtubeid,
                                         gt_id=person.gt_id,
                                         bioguideid=person.bioguideid)
                    rep.save()
                except (CypherException, IOError) as e:
                    logger.exception(e)
                    continue
                if not rep.campaign.all():
                    campaign = PoliticalCampaign(biography=rep.bio,
                                                 youtube=rep.youtube,
                                                 twitter=rep.twitter,
                                                 website=rep.website,
                                                 first_name=rep.first_name,
                                                 last_name=rep.last_name,
                                                 profile_pic=
                                                 settings.STATIC_URL +
                                                 "images/congress/2"
                                                 "25x275/%s.jpg"
                                                 % (rep.bioguideid)).save()
                    campaign.public_official.connect(rep)
                    rep.campaign.connect(campaign)
                    rep.populated_es_index = False
                    rep.save()
                rep.gt_person.connect(person)
                rep.gt_role.connect(role)
                reps.append(rep)
        populate_term_data()
        for rep in reps:
            rep.refresh()
            rep_data = PublicOfficialSerializer(rep).data
            task_data = {
                "object_uuid": rep_data['id'],
                "object_data": rep_data,
            }
            spawn_task(add_object_to_search_index, task_data)

    def handle(self, *args, **options):
        self.create_placeholders()
