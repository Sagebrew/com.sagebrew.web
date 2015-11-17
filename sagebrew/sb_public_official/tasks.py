import us
from celery import shared_task

from py2neo.cypher.error.transaction import ClientError, CouldNotCommit
from neomodel import (db, CypherException, DoesNotExist)

from sb_quests.neo_models import PoliticalCampaign, Position

from .neo_models import PublicOfficial


@shared_task()
def create_and_attach_state_level_reps(rep_data):
    try:
        for representative in rep_data:
            try:
                rep = PublicOfficial.nodes.get(bioguideid=representative['id'])
            except (PublicOfficial.DoesNotExist, DoesNotExist):
                rep = PublicOfficial(gt_id=representative['id'],
                                     bioguideid=representative['id'],
                                     first_name=representative['first_name'],
                                     last_name=representative['last_name'],
                                     middle_name=representative['middle_name'],
                                     state=representative['state'],
                                     state_district=representative['district'],
                                     state_chamber=representative['chamber'],
                                     gov_phone=representative.get(
                                         'office_phone', ''),
                                     full_name=representative.get(
                                         'full_name', '')).save()
            camp = rep.get_campaign()
            if not camp:
                camp = PoliticalCampaign(first_name=rep.first_name,
                                         last_name=rep.last_name,
                                         profile_picture=representative.get(
                                             'photo_url', '')).save()
            rep.campaign.connect(camp)
            camp.public_official.connect(rep)
            query = 'MATCH (l:Location {name:"%s", sector:"federal"})<-' \
                    '[:ENCOMPASSED_BY]-(l2:Location {name:"%s", sector:"%s"})-' \
                    '[:POSITIONS_AVAILABLE]->(p:Position) RETURN p' \
                    % (us.states.lookup(rep.state).name,
                       rep.state_district, 'state_%s' % rep.state_chamber)
            res, _ = db.cypher_query(query)
            if res.one:
                position = Position.inflate(res.one)
                position.campaigns.connect(camp)
                camp.position.connect(position)
        return True
    except (CypherException, ClientError, IOError, CouldNotCommit) as e:
        raise create_and_attach_state_level_reps.retry(exc=e, countdown=5,
                                                       max_retries=None)
