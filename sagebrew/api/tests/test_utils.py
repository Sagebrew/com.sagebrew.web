from uuid import uuid1
from django.test import TestCase

from sb_questions.neo_models import SBQuestion
from api.utils import (add_failure_to_queue, get_object)

'''
We currently do not use the language filter anywhere. We rely on customer
moderation rather than filtering the language used by our customers.
class TestLanguageFilterUtil(TestCase):
    def setUp(self):
        self.vulgar_words = 'anal anus ballsack blowjob blow job boner'

    def test_language_filter(self):
        res = language_filter(self.vulgar_words)

        self.assertNotEqual(res, self.vulgar_words)

    def test_language_filter_not_profane(self):
        sentence = "The quick brown fox jumped over the lazy dog."

        res = language_filter(sentence)

        self.assertEqual(res, sentence)
'''


class TestAddFailureToQueue(TestCase):
    def setUp(self):
        self.message = {
            'message': 'this is a test message to add if a task fails'
        }

    def test_adding_failure_to_queue(self):
        self.assertTrue(add_failure_to_queue(self.message))


class TestGetObject(TestCase):
    def test_bad_class(self):
        question = SBQuestion(question_title='test title for delete',
                              content='this is before delete',
                              object_uuid=str(uuid1())).save()
        test_object = get_object('sb_questions.neo_bad.SBQuestion',
                                 question.object_uuid)

        self.assertFalse(test_object)

    def test_bad_module_class(self):
        question = SBQuestion(question_title='test title for delete',
                              content='this is before delete',
                              object_uuid=str(uuid1())).save()

        test_object = get_object('sb_questions.neo_models.SBQuestionBad',
                                 question.object_uuid)

        self.assertFalse(test_object)

    def test_does_not_exist(self):
        test_uuid = uuid1()
        test_object = get_object('sb_questions.neo_models.SBQuestion',
                                 test_uuid)

        self.assertIsInstance(test_object, Exception)

    def test_valid_object(self):
        question = SBQuestion(question_title='test title for delete',
                              content='this is before delete',
                              object_uuid=str(uuid1())).save()
        test_object = get_object('sb_questions.neo_models.SBQuestion',
                                 question.object_uuid)

        self.assertEqual(test_object.object_uuid, question.object_uuid)

