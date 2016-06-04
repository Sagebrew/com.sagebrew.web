import copy

from django.conf import settings
from django.utils.text import slugify

from neomodel import db

from sb_registration.neo_models import OnboardingTask
from sb_registration.serializers import OnboardingTaskSerializer


def setup_onboarding(quest, mission):
    # Need to copy because in some circumstances the pop action taking place
    # in the for loop removes the element from settings.ONBOARDING_TASKS for
    # good.
    onboarding_tasks = copy.deepcopy(settings.ONBOARDING_TASKS)
    for onboarding_task in onboarding_tasks:
        if onboarding_task['title'] == settings.QUEST_WALLPAPER_TITLE:
            if settings.DEFAULT_WALLPAPER not in quest.wallpaper_pic:
                onboarding_task['completed'] = True
        if onboarding_task['title'] == settings.BANK_SETUP_TITLE:
            if quest.account_verified != "unverified":
                onboarding_task['completed'] = True
        if onboarding_task['title'] == settings.QUEST_ABOUT_TITLE:
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
        # Necessary to ensure independence
        check_query = 'MATCH (mission:Mission {object_uuid: "%s"})' \
                      '-[:MUST_COMPLETE]->' \
                      '(task:OnboardingTask {title: "%s"}) ' \
                      'RETURN task' % (mission.object_uuid,
                                       onboarding_task['title'])
        res, _ = db.cypher_query(check_query)
        if res.one is None:
            # If the task doesn't exist create it
            onboarding_ser = OnboardingTaskSerializer(data=onboarding_task)
            onboarding_ser.is_valid(raise_exception=True)
            onboarding = onboarding_ser.save()
            on_query = 'MATCH (mission:Mission {object_uuid: "%s"}), ' \
                       '(task:OnboardingTask {object_uuid: "%s"}) ' \
                       'CREATE UNIQUE (mission)-[:MUST_COMPLETE]->(task) ' \
                       'RETURN task' % (mission.object_uuid,
                                        onboarding.object_uuid)
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
    completed_sort = []
    uncompleted_sort = []
    for onboarding in onboarding_sort:
        if onboarding['completed']:
            completed_sort.append(onboarding)
            completed_count += 1
        else:
            uncompleted_sort.append(onboarding)
    uncompleted_sort = uncompleted_sort + completed_sort

    return uncompleted_sort, completed_count
