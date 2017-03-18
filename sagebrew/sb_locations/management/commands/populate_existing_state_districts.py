from django.core.management.base import BaseCommand

from sagebrew.api.utils import spawn_task
from sagebrew.sb_address.neo_models import Address
from sagebrew.sb_address.tasks import connect_to_state_districts


class Command(BaseCommand):
    args = "None."

    def populate_state_districts(self):
        for address in Address.nodes.all():
            spawn_task(task_func=connect_to_state_districts,
                       task_param={'object_uuid': address.object_uuid})

    def handle(self, *args, **options):
        self.populate_state_districts()
