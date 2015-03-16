from logging import getLogger
from json import loads

from django.core.management.base import BaseCommand
from django.conf import settings

from neomodel import CypherException, DoesNotExist

from sb_privileges.neo_models import (SBPrivilege, SBRestriction, SBAction)
from sb_requirements.neo_models import SBRequirement


logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates privilege, requirement, action and restrictions.'

    def create_privileges(self):
        with open('%s/sb_privileges/management/commands'
                  '/privilege_nodes.json' % settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            for privilege in data['privileges']:
                requirements = privilege.pop('requirements', [])
                actions = privilege.pop('actions', [])
                try:
                    SBPrivilege.nodes.get(name=privilege[
                        "name"])
                except(SBPrivilege.DoesNotExist, DoesNotExist):
                    try:
                        privilege = SBPrivilege(**privilege).save()
                    except(CypherException, IOError):
                        logger.critical("potential error there may be"
                                        " missing privileges")
                except(CypherException, IOError):
                    logger.critical("potential error there may be "
                                    "missing privileges")
                for requirement in requirements:
                    try:
                        SBRequirement.nodes.get(name=requirement["name"])
                    except(SBRequirement.DoesNotExist, DoesNotExist):
                        try:
                            requirement["url"] = "%s%s" % (settings.WEB_ADDRESS,
                                                           requirement["url"])
                            req = SBRequirement(**requirement).save()
                            privilege.requirements.connect(req)
                        except(CypherException, IOError):
                            logger.critical("potential error there may"
                                            " be missing requirements")
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                                        " be missing requirements")
                for action in actions:
                    try:
                        SBAction.nodes.get(action=action["action"])
                    except(SBAction.DoesNotExist, DoesNotExist):
                        try:
                            action["url"] = "%s%s" % (settings.WEB_ADDRESS,
                                                      action["url"])
                            action = SBAction(**action).save()
                            privilege.actions.connect(action)
                        except(CypherException, IOError):
                            logger.critical("potential error there may"
                                            " be missing actions")
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                                        " be missing actions")
            # for possible future use of single actions not
            # connected with a privilege
            for action in data['actions']:
                try:
                    SBAction.nodes.get(action=action["action"])
                except(SBAction.DoesNotExist, DoesNotExist):
                    try:
                        action["url"] = "%s%s" % (settings.WEB_ADDRESS,
                                                  action["url"])
                        SBAction(**action).save()
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                                         "be missing actions")
                except(CypherException, IOError):
                    logger.critical("potential error there may"
                                    "be missing actions")
            for restriction in data['restrictions']:
                try:
                    SBRestriction.nodes.get(name=restriction["name"])
                except(SBRestriction.DoesNotExist, DoesNotExist):
                    logger.critical("potential error there may"
                          " be missing restrictions")
                try:
                    restriction["url"] = "%s%s" % (settings.WEB_ADDRESS,
                                                   restriction["url"])
                    SBRestriction(**restriction).save()
                except(CypherException, IOError):
                    logger.critical("potential error there may"
                                    " be missing restrictions")

    def handle(self, *args, **options):
        self.create_privileges()
        logger.critical("Created all nodes")