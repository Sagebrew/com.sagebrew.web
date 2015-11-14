from unidecode import unidecode

from celery import shared_task

from py2neo.cypher.error.transaction import ClientError, CouldNotCommit
from neomodel import (db, CypherException, DoesNotExist)

from sb_quests.neo_models import PoliticalCampaign

from .neo_models import PublicOfficial


@shared_task()
def create_and_attach_state_level_reps(rep_data):
    try:
        for rep in rep_data:
            try:
                rep = PublicOfficial.nodes.get(gt_id=rep['id'])
            except (PublicOfficial.DoesNotExist, DoesNotExist):
                rep = PublicOfficial(gt_id=rep['id'], first_name=rep['first_name'],
                                     last_name=rep['last_name'],
                                     middle_name=rep['middle_name'],
                                     state=rep['state'],
                                     state_district=rep['district'],
                                     state_chamber=rep['chamber'],
                                     gov_phone=rep.get('office_phone', ''),
                                     full_name=rep.get('full_name', ''),
                                     image_url=rep.get('photo_url', '')).save()
            camp = rep.get_campaign()
            if not camp:
                camp = PoliticalCampaign(first_name=rep.first_name,
                                         last_name=rep.last_name,
                                         profile_picture=rep.image_url).save()
            rep.campaign.connect(camp)
            camp.public_official.connect(rep)
            return True
    except (CypherException, ClientError, IOError, CouldNotCommit) as e:
        raise create_and_attach_state_level_reps.retry(exc=e, countdown=5,
                                                       max_retries=None)
