from neomodel import (StringProperty, RelationshipTo)

from api.neo_models import SBObject


class Badge(SBObject):
    name = StringProperty()
    image_color = StringProperty()
    image_grey = StringProperty()

    #relationships
    requirements = RelationshipTo('sb_requirements.neo_models.Requirement',
                                  "REQUIRES")


    #methods
    def check_requirements(self, username):
        req_checks = []
        for req in self.get_requirements():
            res = req.check_requirement(username)
            req_checks.append(res['response'])
        if False in req_checks:
            return False
        return True

    def get_dict(self):
        requirements = []
        for req in self.get_requirements():
            requirements.append(req.get_dict())
        return {"image_full": self.image_color,
                "image_grey": self.image_grey,
                "name": self.name,
                "badge_id": self.object_uuid,
                "requirements": requirements}

    def get_requirements(self):
        return self.requirements.all()


class BadgeGroup(SBObject):
    name = StringProperty()
    description = StringProperty()

    #relationships
    badges = RelationshipTo('sb_badges.neo_models.Badge', "HAS")

    #methods
    def get_badges(self):
        return self.badges.all()

    def get_badge_info(self):
        badge_info = {"badges": []}
        for badge in self.get_badges():
            badge_info['badges'].append(badge.get_dict())
        return badge_info