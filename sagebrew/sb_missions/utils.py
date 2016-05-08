from django.conf import settings
from django.utils.text import slugify

from neomodel import db

from sb_registration.neo_models import OnboardingTask
from sb_registration.serializers import OnboardingTaskSerializer

from logging import getLogger
logger = getLogger("loggly_logs")


def setup_onboarding(quest, mission):
    for onboarding_task in settings.ONBOARDING_TASKS:
        if onboarding_task['title'] == "Quest Wallpaper":
            if settings.DEFAULT_WALLPAPER not in quest.wallpaper_pic:
                onboarding_task['completed'] = True
        if onboarding_task['title'] == "Banking Setup":
            if quest.account_verified != "unverified":
                onboarding_task['completed'] = True
        if onboarding_task['title'] == "Quest About":
            if quest.about != "" and quest.about is not None:
                onboarding_task['completed'] = True
        if onboarding_task['type'] == "mission":
            onboarding_task['url'] = onboarding_task['url'] % (
                settings.WEB_ADDRESS,
                mission.object_uuid, slugify(mission.get_mission_title()))
        if onboarding_task['type'] == "quest":
            onboarding_task['url'] = onboarding_task['url'] % (
                settings.WEB_ADDRESS, quest.owner_username)
        onboarding_task.pop('type', None)
        logger.critical(onboarding_task)
        onboarding_ser = OnboardingTaskSerializer(data=onboarding_task)
        onboarding_ser.is_valid(raise_exception=True)
        onboarding = onboarding_ser.save()
        logger.critical("Onboarding: %s" % onboarding.object_uuid)
        logger.critical("Mission: %s" % mission.object_uuid)
        on_query = 'MATCH (mission:Mission {object_uuid: "%s"}), ' \
                   '(task:OnboardingTask {object_uuid: "%s"}) ' \
                   'CREATE UNIQUE (mission)-[:MUST_COMPLETE]->(task) ' \
                   'RETURN task' % (mission.object_uuid,
                                    onboarding.object_uuid)
        logger.critical(on_query)
        db.cypher_query(on_query)
    return True


def order_tasks(mission_id):
    completed_count = 0
    query = 'MATCH (mission:Mission {object_uuid: "%s"})-[:MUST_COMPLETE]' \
            '->(onboarding:OnboardingTask) RETURN onboarding' % mission_id

    res, _ = db.cypher_query(query)
    onboarding_all = OnboardingTaskSerializer(
        [OnboardingTask.inflate(row[0]) for row in res],
        many=True).data
    # Sort the list based on priority
    onboarding_sort = sorted(onboarding_all, key=lambda k: k['priority'])
    # Put the completed tasks at the end of the list
    for idx, onboarding in enumerate(onboarding_sort):
        if onboarding['completed']:
            onboarding_sort.insert(len(onboarding_sort),
                                   onboarding_sort.pop(idx))
            completed_count += 1

    return onboarding_sort, completed_count
