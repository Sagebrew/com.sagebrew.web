from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from govtrack.neo_models import GTRole
from govtrack.utils import populate_term_data
from sb_campaigns.neo_models import PoliticalCampaign
from sb_campaigns.serializers import PoliticalCampaignSerializer

from sb_public_official.neo_models import PublicOfficial

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    help = 'Creates placeholder representatives.'

    def create_placeholders(self):
        camps = []
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
                                         name_mod=person.namemod,
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
                camp = rep.get_campaign()
                if not camp:
                    camp = PoliticalCampaign(biography=rep.bio,
                                             youtube=rep.youtube,
                                             twitter=rep.twitter,
                                             website=rep.website,
                                             first_name=rep.first_name,
                                             last_name=rep.last_name,
                                             profile_pic=settings.
                                             STATIC_URL +
                                             "images/congress/2"
                                             "25x275/%s.jpg"
                                             % (rep.bioguideid)).save()
                    camp.public_official.connect(rep)
                    rep.campaign.connect(camp)
                rep.gt_person.connect(person)
                rep.gt_role.connect(role)
                camps.append(camp)
        populate_term_data()
        for campaign in camps:
            campaign.refresh()
            rep_data = PoliticalCampaignSerializer(campaign).data
            task_data = {
                "object_uuid": rep_data['id'],
                "object_data": rep_data,
            }
            spawn_task(add_object_to_search_index, task_data)

    def handle(self, *args, **options):
        self.create_placeholders()
