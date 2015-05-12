import logging
from django.test import TestCase
from django.core.management import call_command

from sb_public_official.neo_models import PublicOfficial

logger = logging.getLogger('loggly_logs')


class TestCreatePublicOfficialNodes(TestCase):
    def test_create_prepopulated_reps(self):
        call_command("populate_rep_models", True)
        call_command("create_prepopulated_reps")
        test_official = PublicOfficial.nodes.get(gt_id="300093")
        official_terms = test_official.terms
        call_command("create_prepopulated_reps")
        test_official = PublicOfficial.nodes.get(gt_id="300093")
        self.assertEqual(official_terms, test_official.terms)
