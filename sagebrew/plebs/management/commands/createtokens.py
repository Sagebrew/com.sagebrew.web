from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token


class Command(BaseCommand):

    def create_tokens(self):
        """
        This function accesses the local file university_list.csv, converts
        it into a
        dictionary then creates a node of University with the information in
        each dictionary

        :return:
        """

    for user in User.objects.all():
        Token.objects.get_or_create(user=user)

    def handle(self, *args, **options):
        self.create_tokens()
