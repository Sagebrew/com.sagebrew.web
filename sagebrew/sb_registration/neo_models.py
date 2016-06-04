from neomodel import (StringProperty, IntegerProperty, BooleanProperty)

from sb_base.neo_models import TitledContent


class OnboardingTask(TitledContent):
    image_url = StringProperty()
    icon = StringProperty()
    completed = BooleanProperty(default=False)
    completed_title = StringProperty()
    priority = IntegerProperty(default=0)
