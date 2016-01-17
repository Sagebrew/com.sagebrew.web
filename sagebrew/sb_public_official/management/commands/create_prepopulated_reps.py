from logging import getLogger
from localflavor.us.us_states import US_STATES

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import cache

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task
from govtrack.neo_models import GTRole
from govtrack.utils import populate_term_data
from sb_search.tasks import update_search_object
from sb_quests.neo_models import PoliticalCampaign
from sb_quests.serializers import PoliticalCampaignSerializer

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
                    try:
                        state = dict(US_STATES)[role.state]
                    except KeyError:
                        state = role.state
                    rep = PublicOfficial(
                        first_name=person.firstname, last_name=person.lastname,
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
                except (CypherException, IOError) as e:
                    logger.exception(e)
                    continue
                camp = rep.get_campaign()
                if not camp:
                    camp = PoliticalCampaign(
                        biography=rep.bio, youtube=rep.youtube,
                        twitter=rep.twitter, website=rep.website,
                        first_name=rep.first_name, last_name=rep.last_name,
                        profile_pic="%s/representative_images/225x275/"
                                    "%s.jpg" % (
                                        settings.LONG_TERM_STATIC_DOMAIN,
                                        rep.bioguideid)).save()
                    camp.public_official.connect(rep)
                    rep.campaign.connect(camp)
                else:
                    camp.profile_pic = "%s/representative_images/225x275/" \
                                       "%s.jpg" % (
                                           settings.LONG_TERM_STATIC_DOMAIN,
                                           rep.bioguideid)
                    camp.save()
                    cache.set('%s_campaign' % camp.object_uuid, camp)
                rep.gt_person.connect(person)
                rep.gt_role.connect(role)
                camps.append(camp)
        populate_term_data()
        for campaign in camps:
            campaign.refresh()
            rep_data = PoliticalCampaignSerializer(campaign).data
            task_data = {
                "object_uuid": rep_data['id'],
                "instance": campaign,
            }
            spawn_task(update_search_object, task_data)

    def handle(self, *args, **options):
        self.create_placeholders()
