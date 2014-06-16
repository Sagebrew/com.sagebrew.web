from json import dumps

from django.core.management.base import BaseCommand
from django.conf import settings

from plebs.neo_models import TopicCategory, SBTopic


class Command(BaseCommand):
    args = 'None.'
    help = 'Test the conductor api endpoints.'
    sb_categories = [
            {
                "title": "Fiscal/Economy",
                "description": '''Issues involving the Economy,
                        matters of taxation, government spending,
                        importing/exporting, the private sector,
                        wall street etc''',
                "sb_topics": [
                    {
                        "title": "Trade Deficit",
                        "description": "",
                    },
                    {
                        "title": "Deficit Reduction",
                        "description": "",
                    }
                ]
            },
            {
                "title": "Education",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Drugs",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Energy",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Foreign Policy",
                "description": '''Issues involving the interaction between
                                    the Federal Government and Governments of
                                    other states and nations.''',
                "sb_topics": []
            },
            {
                "title": "Science",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Agriculture",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Health",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Social",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Environment",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Defense",
                "description": "",
                "sb_topics": []
            },
            {
                "title": "Space",
                "description": "",
                "sb_topics": []
            }
        ]

    def populate_topic_categories(self):
        for item in self.sb_categories:
            sb_cat = TopicCategory(title=item["title"],
                                   description=item["description"])
            sb_cat.save()
            for topic in item["sb_topics"]:
                try:
                    topic_object = SBTopic.index.get(title=topic["title"])
                except SBTopic.DoesNotExist:
                    topic_object = SBTopic(title=topic["title"],
                                           description=topic["description"])
                    topic_object.save()
                sb_cat.sb_topics.connect(topic_object)


    def handle(self, *args, **options):
        self.populate_topic_categories()
        self.stdout.write("Finished populating categories")
