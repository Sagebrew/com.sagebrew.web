from logging import getLogger

from django.core.management.base import BaseCommand

from neomodel import CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from govtrack.neo_models import GTRole
from sb_docstore.utils import add_object_to_table

from sb_public_official.neo_models import PublicOfficial
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
                    rep = PublicOfficial(first_name=person.firstname,
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
                                       terms=len(role.congress_numbers.all()),
                                       twitter=person.twitterid,
                                       youtube=person.youtubeid)
                    rep.save()
                    reps.append(rep)
                    rep.gt_person.connect(person)
                    rep.gt_role.connect(role)
                except (CypherException, IOError) as e:
                    logger.exception(e)
                    continue
        for rep in reps:
            rep_data = PublicOfficialSerializer(rep).data
            add_object_to_table("general_reps", rep_data)
            task_data = {
                "object_type": "sagas",
                "object_data": rep_data
            }
            spawn_task(add_object_to_search_index, task_data)

    def handle(self, *args, **options):
        self.create_placeholders()
