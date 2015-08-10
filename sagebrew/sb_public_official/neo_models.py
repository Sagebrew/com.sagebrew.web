from neomodel import (StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, db)

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
    # address and contact form are gained from the term data and they will be
    # updated to their current office address and their current contact form
    address = StringProperty()
    contact_form = StringProperty()
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
    # the current term is also included in the number of terms under the term
    # relationship, the current_term relationship is a shortcut for us to
    # access the term that the official is currently in
    term = RelationshipTo('govtrack.neo_models.Term', 'SERVED_TERM')
    current_term = RelationshipTo('govtrack.neo_models.Term', 'CURRENT_TERM')
    campaign = RelationshipTo('sb_campaigns.neo_models.PoliticalCampaign',
                              'HAS_CAMPAIGN')

    def get_campaign(self):
        from sb_campaigns.neo_models import PoliticalCampaign
        query = 'MATCH (o:PublicOfficial {object_uuid:"%s"})-' \
                '[:HAS_CAMPAIGN]->(c:PoliticalCampaign) RETURN c' \
                % self.object_uuid
        res, _ = db.cypher_query(query)
        try:
            campaign = PoliticalCampaign.inflate(res[0][0])
        except IndexError:
            campaign = None
        return campaign


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
