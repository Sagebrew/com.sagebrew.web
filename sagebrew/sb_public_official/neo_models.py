from neomodel import (StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from sb_search.neo_models import Searchable


class CongressVoteRelationship(StructuredRel):
    pass


class PublicOfficial(Searchable):
    """
    The PublicOfficial does not inherit from Pleb as Plebs must be associated
    with a user. PublicOfficial is a node that is dynamically populated based
    on our integrations with external services. It cannot be modified by
    users of the web app. Plebs can be attached to a PublicOfficial though
    if they are that individual. Public Officials should also always be
    available whether or not a user exits or joins the system so that we can
    always make the public information known and populate action areas
    for officials that are not yet signed up.
    """
    first_name = StringProperty()
    last_name = StringProperty()
    middle_name = StringProperty()
    gender = StringProperty()
    date_of_birth = DateTimeProperty()
    gt_id = StringProperty(index=True)
    title = StringProperty()
    bio = StringProperty(default="")
    name_mod = StringProperty()
    current = BooleanProperty()
    district = IntegerProperty(default=0)
    state = StringProperty()
    website = StringProperty()
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()
    full_name = StringProperty()
    gov_phone = StringProperty()
    # recipient_id and customer_id are stripe specific attributes
    recipient_id = StringProperty()
    customer_id = StringProperty()
    terms = IntegerProperty()
    twitter = StringProperty()
    youtube = StringProperty()
    bioguideid = StringProperty(unique_index=True)
    # bioguide is used to get the reps public profile picture

    # relationships
    pleb = RelationshipTo('plebs.neo_models.Pleb', 'AUTHORIZED_AS')
    # sponsored = RelationshipTo('sb_public_official.neo_models.Bill',
    #                            "SPONSORED")
    # co_sponsored = RelationshipTo('sb_public_official.neo_models.Bill',
    #                               "COSPONSORED")
    # proposed = RelationshipTo('sb_public_official.neo_models.Bill',
    #                           "PROPOSED")
    # hearings = RelationshipTo('sb_public_official.neo_models.Hearing',
    #                           "ATTENDED")
    # experience = RelationshipTo('sb_public_official.neo_models.Experience',
    #                             "EXPERIENCED")
    gt_person = RelationshipTo('govtrack.neo_models.GTPerson', 'GTPERSON')
    gt_role = RelationshipTo('govtrack.neo_models.GTRole', 'GTROLE')

    def get_dict(self):
        crop_name = str(self.full_name).rfind('[')
        try:
            full_name = self.full_name[:crop_name]
        except IndexError:
            full_name = self.full_name
        try:
            bioguideid = self.gt_person.all()[0].bioguideid
        except IndexError:
            bioguideid = None
        return {
            "object_uuid": self.object_uuid,
            "full_name": full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "start_date": unicode(self.start_date),
            "end_date": unicode(self.end_date),
            "state": self.state,
            "title": self.title,
            "district": self.district,
            "current": self.current,
            "bioguide": bioguideid,
            "terms": self.terms,
            "youtube": self.youtube,
            "twitter": self.twitter,
            "channel_wallpaper": None
        }

'''
class Bill(StructuredNode):
    bill_id = StringProperty(unique_index=True)

    # relationships
    proposer = RelationshipTo(PublicOfficial, "PROPOSED_BY")
    sponsor = RelationshipTo(PublicOfficial, "SPONSORED_BY")
    co_sponsor = RelationshipTo(PublicOfficial, "COSPONSORED_BY")


class Hearing(StructuredNode):
    hearing_id = StringProperty(unique_index=True)

    # relationships
    attendees = RelationshipTo(PublicOfficial, "HEARING_ATTENDEES")


class Committee(StructuredNode):
    committee_number = IntegerProperty(unique_index=True)

    # relationships
    members = RelationshipTo(PublicOfficial, "COMMITTEE_MEMBERS")
'''
