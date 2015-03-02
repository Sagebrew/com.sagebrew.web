from logging import getLogger
from json import loads

from django.core.management.base import BaseCommand
from django.conf import settings

from neomodel import CypherException, DoesNotExist

from sb_privileges.neo_models import (SBPrivilege, SBRestriction, SBAction)
from sb_requirements.neo_models import Requirement


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
                    SBPrivilege.nodes.get(privilege_name=privilege[
                        "privilege_name"])
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
                        Requirement.nodes.get(key=requirement["total_rep"])
                    except(Requirement.DoesNotExist, DoesNotExist):
                        try:
                            req = Requirement(**requirement).save()
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
                            action = SBAction(**action).save()
                            privilege.actions.connect(action)
                        except(CypherException, IOError):
                            logger.critical("potential error there may"
                                  " be missing actions")
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                              " be missing actions")
            #for possible future use of single actions not
            # connected with a privilege
            for action in data['actions']:
                try:
                    SBAction.nodes.get(action=action["action"])
                except(SBAction.DoesNotExist, DoesNotExist):
                    try:
                        action = SBAction(**action).save()
                    except(CypherException, IOError):
                        logger.critical("potential error there may"
                              " be missing actions")
                except(CypherException, IOError):
                    logger.critical("potential error there may"
                          " be missing actions")
            for restriction in data['restrictions']:
                try:
                    SBRestriction.nodes.get(name="name")
                except(SBRestriction.DoesNotExist, DoesNotExist):
                    logger.critical("potential error there may"
                          " be missing restrictions")
                try:
                    restriction = SBRestriction(**restriction).save()
                except(CypherException, IOError):
                    logger.critical("potential error there may"
                          " be missing restrictions")


    def handle(self, *args, **options):
        self.create_privileges()
        logger.critical("Created all nodes")