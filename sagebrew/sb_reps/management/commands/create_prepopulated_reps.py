from logging import getLogger

from django.core.management.base import BaseCommand

from neomodel import CypherException

from govtrack.neo_models import  GTRole
from sb_reps.neo_models import BaseOfficial

logger = getLogger('loggly_logs')

class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def create_placeholders(self):
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
                    rep = BaseOfficial(first_name=person.firstname,
                                       last_name=person.lastname,
                                       gender=person.gender,
                                       date_of_birth=person.birthday,
                                       namemod=person.namemod,
                                       current=role.current,
                                       bio=role.description,
                                       district=role.district,
                                       state=role.state,
                                       title=role.title,
                                       website=role.website,
                                       start_date=role.startdate,
                                       end_date=role.enddate)
                    rep.save()
                except (CypherException, IOError) as e:
                    logger.exception(e)
                    continue


    def handle(self, *args, **options):
        self.create_placeholders()
