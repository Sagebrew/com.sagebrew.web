from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import db

from sagebrew.plebs.neo_models import Pleb
from sagebrew.sb_tags.neo_models import Tag
from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_questions.neo_models import Question
from sagebrew.sb_solutions.neo_models import Solution
from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_quests.neo_models import Quest


class TestQuestionNeoModel(TestCase):

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content='test content',
                                 object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username,
                                 title=str(uuid1())).save()
        self.question.owned_by.connect(self.pleb)

    def test_add_no_auto_tags(self):
        res = self.question.add_auto_tags([])
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 0)

    def test_add_auto_tags(self):
        auto_tags = [{'tags': {'text': 'testautotag', 'relevance': 0.10201}}]
        res = self.question.add_auto_tags(auto_tags)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].name, 'testautotag')

    def test_add_multiple_auto_tags(self):
        auto_tags = [{'tags': {'text': 'testautotag4', 'relevance': 0.10201}},
                     {'tags': {'text': 'testautotag8', 'relevance': 0.10441}}]
        res = self.question.add_auto_tags(auto_tags)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].name, 'testautotag4')
        self.assertEqual(res[1].name, 'testautotag8')

    def test_add_multiple_auto_tags_not_unique(self):
        auto_tags = [{'tags': {'text': 'testautotag6', 'relevance': 0.10201}},
                     {'tags': {'text': 'testautotag6', 'relevance': 0.10441}}]
        res = self.question.add_auto_tags(auto_tags)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].name, 'testautotag6')
        self.assertEqual(res[0].object_uuid, res[1].object_uuid)

    def test_empty_get_tags_string(self):
        res = self.question.get_tags_string()

        self.assertEqual(res, "")

    def test_empty_get_one_tag_string(self):
        tag = Tag(name=str(uuid1())).save()
        self.question.tags.connect(tag)
        res = self.question.get_tags_string()
        self.question.tags.disconnect(tag)
        self.assertEqual(res, "%s" % tag.name)

    def test_empty_get_multiple_tag_string(self):
        tag = Tag(name=str(uuid1())).save()
        tag2 = Tag(name=str(uuid1())).save()
        self.question.tags.connect(tag)
        self.question.tags.connect(tag2)
        res = self.question.get_tags_string()
        self.question.tags.disconnect(tag)
        self.question.tags.disconnect(tag2)
        self.assertIn(tag.name, res)
        self.assertIn(tag2.name, res)
        self.assertIn(',', res)

    def test_question_author(self):
        authors = self.question.get_conversation_authors()
        self.assertEqual("%s %s" % (self.pleb.first_name, self.pleb.last_name),
                         authors)

    def test_one_solution_by_same_author(self):
        solution = Solution(content=uuid1(),
                            owner_username=self.pleb.username).save()
        self.question.solutions.connect(solution)
        authors = self.question.get_conversation_authors()
        self.assertEqual("%s %s" % (self.pleb.first_name, self.pleb.last_name),
                         authors)

    def test_two_solutions_different_authors(self):
        pleb = Pleb(email=str(uuid1()), first_name="test",
                    last_name="test", username=str(uuid1())).save()
        solution = Solution(content=uuid1(),
                            owner_username=self.pleb.username).save()
        solution2 = Solution(content=uuid1(),
                             owner_username=pleb.username).save()
        self.question.solutions.connect(solution)
        self.question.solutions.connect(solution2)
        authors = self.question.get_conversation_authors()
        self.assertIn(self.pleb.first_name, authors)
        self.assertIn(self.pleb.last_name, authors)
        self.assertIn(pleb.first_name, authors)
        self.assertIn(pleb.last_name, authors)
        self.assertEqual(authors.count(','), 1)

    def test_three_solutions_different_authors(self):
        pleb = Pleb(email=str(uuid1()), first_name="test",
                    last_name="test", username=str(uuid1())).save()
        pleb2 = Pleb(email=str(uuid1()), first_name="test",
                     last_name="test", username=str(uuid1())).save()
        solution = Solution(content=uuid1(),
                            owner_username=self.pleb.username).save()
        solution2 = Solution(content=uuid1(),
                             owner_username=pleb.username).save()
        solution3 = Solution(content=uuid1(),
                             owner_username=pleb2.username).save()
        self.question.solutions.connect(solution)
        self.question.solutions.connect(solution2)
        self.question.solutions.connect(solution3)
        authors = self.question.get_conversation_authors()
        self.assertIn(self.pleb.first_name, authors)
        self.assertIn(self.pleb.last_name, authors)
        self.assertIn(pleb.first_name, authors)
        self.assertIn(pleb.last_name, authors)
        self.assertIn(pleb2.first_name, authors)
        self.assertIn(pleb2.last_name, authors)
        self.assertEqual(authors.count(','), 2)

    def test_get_solution_ids(self):
        query = 'MATCH (n:Solution) OPTIONAL MATCH (n)-[r]-() DELETE n, r'
        db.cypher_query(query)
        pleb = Pleb(email=str(uuid1()), first_name="test",
                    last_name="test", username=str(uuid1())).save()
        pleb2 = Pleb(email=str(uuid1()), first_name="test",
                     last_name="test", username=str(uuid1())).save()
        solution = Solution(content=uuid1(),
                            owner_username=self.pleb.username).save()
        solution2 = Solution(content=uuid1(),
                             owner_username=pleb.username).save()
        solution3 = Solution(content=uuid1(),
                             owner_username=pleb2.username).save()
        self.question.solutions.connect(solution)
        self.question.solutions.connect(solution2)
        self.question.solutions.connect(solution3)
        solutions = self.question.get_solution_ids()
        self.assertEqual(len(solutions), 3)
        self.assertIn(solution.object_uuid, solutions)
        self.assertIn(solution2.object_uuid, solutions)
        self.assertIn(solution3.object_uuid, solutions)

    def test_get_mission(self):
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        mission.associated_with.connect(self.question)
        res = Question.get_mission(self.question.object_uuid)
        self.assertEqual(res['id'], mission.object_uuid)
        mission.delete()
        quest.delete()
