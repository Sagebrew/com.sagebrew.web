from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.neo_models import Pleb
from sb_posts.neo_models import SBPost
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion
from sb_search.tasks import update_weight_relationship

class TestUpdateWeightRelationshipTaskQuestion(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)
        self.question = SBQuestion(question_id=str(uuid1()))

    def tearDown(self):
        call_command('clear_neo_db')

class TestUpdateWeightRelationshipTaskPleb(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)
        self.user2 = User.objects.create_user(
            username='Tyler2', email=str(uuid1())+'@gmail.com')
        self.pleb2 = Pleb.nodes.get(email=self.user2.email)

    def tearDown(self):
        call_command('clear_neo_db')

class TestUpdateWeightRelationshipTaskPost(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)
        self.user2 = User.objects.create_user(
            username='Tyler2', email=str(uuid1())+'@gmail.com')
        self.pleb2 = Pleb.nodes.get(email=self.user2.email)

    def tearDown(self):
        call_command('clear_neo_db')

class TestUpdateWeightRelationshipTaskAnswer(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)
        self.user2 = User.objects.create_user(
            username='Tyler2', email=str(uuid1())+'@gmail.com')
        self.pleb2 = Pleb.nodes.get(email=self.user2.email)

    def tearDown(self):
        call_command('clear_neo_db')