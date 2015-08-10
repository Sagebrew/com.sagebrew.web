import os
from logging import getLogger
from json import loads

from django.core.management.base import BaseCommand
from django.conf import settings

from rest_framework.reverse import reverse, NoReverseMatch

from neomodel import CypherException, DoesNotExist

from sb_privileges.neo_models import (Privilege, Restriction, SBAction)
from sb_requirements.neo_models import Requirement


logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates privilege, requirement, action and restrictions.'

    def create_privileges(self):
        with open('%s/sb_privileges/management/commands'
                  '/privilege_nodes.json' % settings.PROJECT_DIR) as data_file:
            data = loads(data_file.read())
            for privilege in data['privileges']:
                requirements = privilege.pop('requirements', [])
                actions = privilege.pop('actions', [])
                try:
                    privilege_obj = Privilege.nodes.get(name=privilege["name"])
                except(Privilege.DoesNotExist, DoesNotExist):
                    try:
                        privilege_obj = Privilege(**privilege).save()
                    except(CypherException, IOError):
                        logger.critical("potential error there may be"
                                        " missing privileges")
                except(CypherException, IOError):
                    logger.critical("potential error there may be "
                                    "missing privileges")
                for requirement in requirements:
                    try:
                        req = Requirement.nodes.get(name=requirement["name"])
                        privilege_obj.requirements.connect(req)
                    except(Requirement.DoesNotExist, DoesNotExist):
                        try:
                            requirement["url"] = "%s%s" % (settings.WEB_ADDRESS,
                                                           requirement["url"])
                            req = Requirement(**requirement).save()
                            privilege_obj.requirements.connect(req)
                        except(CypherException, IOError):
                            logger.critical("potential error there may"
                                            " be missing requirements")
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                                        " be missing requirements")
                action_obj = None
                for action in actions:
                    action_resource = "%s-list" % action["resource"]
                    try:
                        action_url = reverse(action_resource)
                    except NoReverseMatch:
                        action_url = "/%s" % action["resource"]
                    if "http" not in action_url:
                        branch = os.environ.get("CIRCLE_BRANCH", None)
                        circle_ci = os.environ.get("CIRCLECI", "false").lower()
                        if circle_ci == "false":
                            circle_ci = False
                        if circle_ci == "true":
                            circle_ci = True

                        if circle_ci is True:
                            action_url = "https://localhost%s" % action_url
                        elif branch is None:
                            action_url = "https://localhost%s" % action_url
                        elif "dev" in branch:
                            action_url = "https://localhost%s" % action_url
                        elif branch == "staging":
                            action_url = "https://staging.sagebrew.com%s" % (
                                action_url)
                        elif branch == "master":
                            action_url = "http://www.sagebrew.com%s" % (
                                action_url)
                        else:
                            action_url = "http://www.sagebrew.com%s" % (
                                action_url)
                    try:
                        # Note that this will not always be a unique index and
                        # may require some tweeking in the future
                        action_obj = SBAction.nodes.get(url=action_url)
                    except(SBAction.DoesNotExist, DoesNotExist):
                        try:
                            action["url"] = action_url
                            action_obj = SBAction(**action).save()
                        except(CypherException, IOError):
                            logger.critical("potential error there may"
                                            " be missing actions")
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                                        " be missing actions")
                    if action_obj is not None:
                        privilege_obj.actions.connect(action_obj)
                    action_obj = None
            for restriction in data['restrictions']:
                try:
                    Restriction.nodes.get(name=restriction["name"])
                except(Restriction.DoesNotExist, DoesNotExist):
                    try:
                        restriction["url"] = "%s%s" % (settings.WEB_ADDRESS,
                                                       restriction["url"])
                        Restriction(**restriction).save()
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                                        " be missing restrictions")

    def handle(self, *args, **options):
        self.create_privileges()
        logger.critical("Created all nodes")
