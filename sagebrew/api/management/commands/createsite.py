from django.core.management.base import BaseCommand
import os

from django.contrib.sites.models import Site


class Command(BaseCommand):
    args = 'None.'

    def populate_base_tags(self):
        branch = os.environ.get("CIRCLE_BRANCH", None)
        circle_ci = os.environ.get("CIRCLECI", False)
        if circle_ci == "false":
            circle_ci = False
        if circle_ci == "true":
            circle_ci = True

        if circle_ci is True:
            domain = "localhost"
        elif branch is None:
            domain = "192.168.56.101"
        elif "dev" in branch:
            domain = "192.168.56.101"
        elif branch == "staging":
            domain = "staging.sagebrew.com"
        elif branch == "master":
            domain = "www.sagebrew.com"
        else:
            domain = "www.sagebrew.com"

        site = Site.objects.get(pk=1)
        site.name = domain
        site.domain = domain
        site.save()

    def handle(self, *args, **options):
        self.populate_base_tags()
