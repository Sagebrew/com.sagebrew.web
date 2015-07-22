from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token


class Command(BaseCommand):

    def create_tokens(self):
        for user in User.objects.all():
            Token.objects.get_or_create(user=user)

    def handle(self, *args, **options):
        self.create_tokens()
