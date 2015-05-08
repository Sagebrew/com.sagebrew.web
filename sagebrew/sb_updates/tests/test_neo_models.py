from uuid import uuid1

from django.test import TestCase

from sb_campaigns.neo_models import Campaign
from sb_goals.neo_models import Goal

from sb_updates.neo_models import Update


class TestUpdateNeoModel(TestCase):
    def setUp(self):
        self.campaign = Campaign(stripe_id=str(uuid1())).save()

    def test_create_update(self):
        goal = Goal(title="Save the world",
                    summary="I'll be saving the world by rescuing the polar"
                            "bears.",
                    description="To save the world we must save the polar"
                                "bears. This is because they are an essential"
                                "part to our day to day lives and ensure the"
                                "polar ice caps stay clean.",
                    pledged_vote_requirement=5,
                    monetary_requirement=100).save()
        goal.campaign.connect(self.campaign)
        self.campaign.goals.connect(goal)
        content = "Here is an update on rescuing the polar" \
                  " bears. I was able to raise the necessary" \
                  " $100 thanks to all my supporters. This " \
                  "was then used to Save the world. And here " \
                  "is a video to show how happy the world is " \
                  "now that the polar bears are alive!"
        object_uuid = str(uuid1())
        update = Update(object_uuid=object_uuid, content=content).save()
        update.campaign.connect(self.campaign)
        update.goals.connect(goal)
        goal.updates.connect(update)
        self.campaign.updates.connect(update)

        update_query = Update.nodes.get(object_uuid=object_uuid)
        self.assertIn(update_query.content, content)
