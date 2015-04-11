from uuid import uuid1
from logging import getLogger

from django.core.management.base import BaseCommand

from neomodel import CypherException

from govtrack.neo_models import  GTRole
from sb_docstore.utils import add_object_to_table
from sb_public_official.neo_models import BaseOfficial
from sb_public_official.serializers import PublicOfficialSerializer


logger = getLogger('loggly_logs')

class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def create_placeholders(self):
        reps = []
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
                                       end_date=role.enddate,
                                       full_name=person.name,
                                       object_uuid=str(uuid1()))
                    rep.save()
                    reps.append(rep)
                except (CypherException, IOError) as e:
                    logger.exception(e)
                    continue
        for rep in reps:
            rep_data = PublicOfficialSerializer(rep).data
            add_object_to_table("general_reps", rep_data)


    def handle(self, *args, **options):
        self.create_placeholders()
