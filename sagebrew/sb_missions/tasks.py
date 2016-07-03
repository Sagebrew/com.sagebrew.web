from celery import shared_task

from neomodel import db

from sb_base.serializers import IntercomEventSerializer

from .neo_models import Mission


@shared_task()
def send_reengage_message(mission_uuid, mission_type):
    query = 'MATCH (mission:Mission {object_uuid: "%s"}) ' \
            'WHERE mission.submitted_for_review=FALSE ' \
            'RETURN mission' % mission_uuid
    res, _ = db.cypher_query(query)
    print(res.one)
    if res.one is not None:
        # Trigger an event rather than send an email because intercom
        # only allows us to send personal or plain emails through the
        # api.
        mission = Mission.inflate(res.one)
        event_name = 'fifteen-minute-reengage'
        if mission_type == "advocacy":
            event_name = "fifteen-minute-reengage-advocacy"
        elif mission_type == "position":
            event_name = "fifteen-minute-reengage-public-office"
        data = {
            "event_name": event_name,
            "username": mission.owner_username
        }
        serializer = IntercomEventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
    return True
