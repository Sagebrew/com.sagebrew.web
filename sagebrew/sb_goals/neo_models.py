import pytz
from datetime import datetime

from py2neo.cypher import ClientError
from neomodel import (db, StringProperty, IntegerProperty, DoesNotExist,
                      BooleanProperty, RelationshipTo, DateTimeProperty,
                      CypherException)

from api.neo_models import SBObject
from api.utils import spawn_task, deprecation
from sb_quests.tasks import release_funds_task


class Goal(SBObject):
    """
    Goals are milestones set by campaigning individuals in an attempt to raise
    funds. Goals must have a monetary requirement and can have a
    pledged vote requirement. These are used to manage when donations will
    actually be billed against the user and given to the representative.
    Each goal should set a tangible achievement that can be obtained based on
    the requirements set. Each goal must also have an update associated with it
    after it has been reached. This way users can have some transparency as to
    how their donations are actually being used.
    Goals are organized into rounds in an attempt to make the assignment process
    more agile and reduce the strain on users of having to define all their
    goals up front.
    """
    # This is what will be shown above each goal in the Action area. Titles
    # should describe what the goal is for in a couple words, around 40 chars.
    # Required
    title = StringProperty()
    # Summary is used to provide a summary of the description and should
    # lay out what the goal is attempting to accomplish in 300 or so characters.
    # This is may be shown in the Action area and can potentially be utilized
    # when a user clicks on a goal and is about to donate to it.
    # Required
    summary = StringProperty()
    # Description is the longer explanation of what the goal entails and why
    # it's being done. This may not be shown initially and can be optional.
    # We can provide this as the markdown area where a campaigner can go into
    # great detail regarding a given goal.
    # Optional
    description = StringProperty()
    pledged_vote_requirement = IntegerProperty(default=0)
    monetary_requirement = IntegerProperty(default=0)
    completed = BooleanProperty(default=False)
    completed_date = DateTimeProperty()
    # total_required represents the total amount of donations required to
    # complete the goal
    total_required = IntegerProperty()
    # pledges_required represents the total amount of pledges required to
    # complete the goal
    pledges_required = IntegerProperty()
    # target is an optimization property we use when rendering templates
    # for a quest page
    target = BooleanProperty(default=False)

    # optimizations
    # Active is automatically set when the round the goal is in is taken active
    # This allows us to validate whether or not a goal can be changed by
    # looking directly at it rather than having to query up to the round.
    active = BooleanProperty(default=False)
    # campaign_id allows us to have one less query when updating a goal and
    # allows us to not have to worry about passing campaign to update method,
    # the object knows which campaign it is owned by
    campaign_id = StringProperty()

    # relationships
    updates = RelationshipTo('sb_updates.neo_models.Update', "UPDATE_FOR")
    donations = RelationshipTo('sb_donations.neo_models.Donation', "RECEIVED")
    previous_goal = RelationshipTo('sb_goals.neo_models.Goal', "PREVIOUS")
    next_goal = RelationshipTo('sb_goals.neo_models.Goal', "NEXT")

    # DEPRECATIONS
    # DEPRECATED: Goals are no longer directly associated with Quests. Instead
    # they are associated with Missions. Use "WORKING_TOWARDS" off of a mission
    # to determine the Goals
    campaign = RelationshipTo('sb_quests.neo_models.Campaign',
                              'ASSOCIATED_WITH')

    # DEPRECATED: Rounds are no longer used. Instead Goals are either active
    # or not and are not grouped into any specific "round"
    associated_round = RelationshipTo('sb_goals.neo_models.Round', "PART_OF")

    @classmethod
    def get_updates(cls, object_uuid):
        query = 'MATCH (g:`Goal` {object_uuid: "%s"})-[:UPDATE_FOR]->' \
                '(u:`Update`) return u.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_donations(cls, object_uuid):
        query = 'MATCH (g:`Goal` {object_uuid: "%s"})-[:RECEIVED]->' \
                '(u:`Donation`) return u.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_associated_round(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (g:`Goal` {object_uuid: "%s"})-[:PART_OF]->' \
                '(u:`Round`) return u.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None

    @classmethod
    def get_previous_goal(cls, object_uuid):
        query = 'MATCH (g:`Goal` {object_uuid: "%s"})-[:PREVIOUS]->' \
                '(u:`Goal`) return u.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None

    @classmethod
    def get_next_goal(cls, object_uuid):
        query = 'MATCH (g:`Goal` {object_uuid: "%s"})-[:NEXT]->' \
                '(u:`Goal`) return u.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None

    @classmethod
    def get_campaign(cls, object_uuid):
        # DEPRECATED use get_mission or get_quest instead
        deprecation('Campaigns are deprecated, use Missions or Quests instead')
        query = 'MATCH (g:`Goal` {object_uuid: "%s"})-[:ASSOCIATED_WITH]-' \
                '(c:`Campaign`) RETURN c.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None

    @classmethod
    def get_associated_round_donation_total(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (g:Goal {object_uuid: "%s"})-[:PART_OF]->(r:Round)-' \
                '[:HAS_DONATIONS]->(d:Donation) RETURN sum(d.amount)' \
                % object_uuid
        res, _ = db.cypher_query(query)
        return res.one

    def disconnect_from_upcoming(self):
        query = 'OPTIONAL MATCH (g:Goal {object_uuid: "%s"})-' \
                '[:PART_OF]->(r:Round) RETURN r' % self.object_uuid
        res, _ = db.cypher_query(query)
        associated_round = res.one
        if associated_round:
            associated_round = Round.inflate(associated_round)
            self.associated_round.disconnect(associated_round)
            associated_round.goals.disconnect(self)
        return True

    def check_for_update(self):
        query = 'MATCH (g:Goal {object_uuid: "%s"})-[:UPDATE_FOR]->' \
                '(u:Update) RETURN u'
        res, _ = db.cypher_query(query)
        if not res.one:
            return False
        return True


class Round(SBObject):
    """
    !!!!!!!!!DEPRECATED!!!!!!!!!
    A round is a grouping of goals. The objective of a round is to provide
    more of an agile development feel to the goal assignment process. A round
    is much like a sprint only over a much longer duration. But within it
    the user defines which goals they'd like to accomplish and how much they'll
    need to raise to accomplish each. Then they can try and close out that
    round by achieving each of the goals, providing updates, and then start
    a new round.

    NOTE: Please be aware that you should not use `round` when instantiating
    this object. `round` is a keyword in Python relating to rounding. Please
    use something else to store the instance in.
    """
    # Start date should not be confused with `created` created is when the user
    # first defines the round, while start date is the day it goes public.
    # This gives us some flexibility with enabling users to set a time in the
    # future they would like the round to go active.
    start_date = DateTimeProperty()
    # Completed is a programmaticly set value that should be set when
    # the campaigner closes out a round by completing all the associated
    # goals.
    # Completed should be used to check if the round is historical. This is
    # set to null when it has not yet been started and/or it is the currently
    # active round.
    completed = DateTimeProperty()
    active = BooleanProperty(default=False)
    queued = BooleanProperty(default=False)
    # queued is an optimization added to allow us to easily determine
    # whether or not the round should be moved into the active round
    # position on completion of the currently active round.

    # relationships
    goals = RelationshipTo('sb_goals.neo_models.Goal', "STRIVING_FOR")
    donations = RelationshipTo('sb_donations.neo_models.Donation',
                               "HAS_DONATIONS")
    previous_round = RelationshipTo('sb_goals.neo_models.Round', "PREVIOUS")
    next_round = RelationshipTo('sb_goals.neo_models.Round', "NEXT")
    campaign = RelationshipTo('sb_quests.neo_models.Campaign',
                              'ASSOCIATED_WITH')

    @classmethod
    def get_goals(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (r:`Round` {object_uuid:"%s"})-[:STRIVING_FOR]->' \
                '(g:`Goal`) RETURN g.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_previous_round(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (r:`Round` {object_uuid:"%s"})-[:PREVIOUS]->' \
                '(g:`Round`) RETURN g.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None

    @classmethod
    def get_next_round(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (r:`Round` {object_uuid:"%s"})-[:NEXT]->' \
                '(g:`Round`) RETURN g.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None

    @classmethod
    def get_campaign(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (r:Round {object_uuid:"%s"})-[:ASSOCIATED_WITH]->' \
                '(c:Campaign) RETURN c.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None

    @classmethod
    def get_total_donation_amount(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (r:Round {object_uuid:"%s"})-[:HAS_DONATIONS]->' \
                '(d:Donation) RETURN sum(d.amount)' % object_uuid
        res, _ = db.cypher_query(query)
        return res.one

    def check_goal_completion(self):
        """
        This loops through all goals connected to the round to see if
        they are now completed with the current donation total and pledge vote
        and if they have an update, if all of these are true the goal is
        labeled as completed and sets the goal attached to it via the next_goal
        relationship to the current target goal. It then checks to see if the
        round is completed.
        :return:
        """
        from sb_quests.neo_models import PoliticalCampaign
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (r:`Round` {object_uuid:"%s"})-[:STRIVING_FOR]->' \
                '(g:`Goal`) WITH r, g MATCH ' \
                '(r)-[:ASSOCIATED_WITH]->(c:Campaign) ' \
                'RETURN g, c.object_uuid' % self.object_uuid
        res, _ = db.cypher_query(query)
        total_donations = Round.get_total_donation_amount(self.object_uuid)
        try:
            try:
                total_pledges = PoliticalCampaign.get_vote_count(res[0][1])
            except IndexError:
                total_pledges = 0
            for goal in res:
                goal_node = Goal.inflate(goal[0])
                try:
                    prev_goal = Goal.nodes.get(
                        object_uuid=Goal.get_previous_goal(
                            goal_node.object_uuid))
                    update_provided = prev_goal.check_for_update()
                except (Goal.DoesNotExist, DoesNotExist):
                    update_provided = True

                if total_donations >= goal_node.total_required \
                        and total_pledges >= goal_node.pledges_required \
                        and update_provided:
                    # update must be provided for the goal to be completed
                    goal_node.completed = True
                    goal_node.completed_date = datetime.now(pytz.utc)
                    goal_node.save()
                    spawn_task(task_func=release_funds_task,
                               task_param={"goal_uuid": goal_node.object_uuid})
                    try:
                        next_goal = Goal.nodes.get(
                            object_uuid=Goal.get_next_goal(
                                goal_node.object_uuid))
                        next_goal.target = True
                    except (Goal.DoesNotExist, DoesNotExist):
                        pass
            self.check_round_completion()
            return True
        except (CypherException, IOError, ClientError) as e:
            return e

    def check_round_completion(self):
        """
        This util checks to see if every goal attached to the round is
        completed. If all of the goals are completed, it changes the current
        round to inactive. It then checks if there is a round attached to
        the upcoming round that is queued, if there is then it move that round
        to the currently active round relationship with the campaign.
        :return:
        """
        from sb_quests.neo_models import PoliticalCampaign
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (r:Round {object_uuid:"%s"})-[:STRIVING_FOR]->' \
                '(g:Goal) WITH r, g MATCH (r)-[ASSOCIATED_WITH]->' \
                '(c:Campaign) RETURN g.completed, c.object_uuid ' \
                % self.object_uuid
        res, _ = db.cypher_query(query)
        if False not in [row[0] for row in res]:
            campaign = PoliticalCampaign.get(res[0][1])
            upcoming_round = Round.nodes.get(
                object_uuid=PoliticalCampaign.get_upcoming_round(
                    campaign.object_uuid))
            if upcoming_round.queued:
                campaign.active_round.disconnect(self)
                self.active = False
                self.completed = datetime.now(pytz.utc)
                self.save()
                campaign.active_round.connect(upcoming_round)
                upcoming_round.active = True
                upcoming_round.save()
                new_round = Round().save()  # create new upcoming round
                campaign.upcoming_round.connect(new_round)
                new_round.campaign.connect(campaign)
        return True
