from django.contrib import sitemaps
from django.core.urlresolvers import reverse


class AccountHelpSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['delete_account', 'reset_password', 'create_an_account',
                'restriction_on_asking']

    def location(self, item):
        return reverse(item)


class ConversationHelpSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['closed', 'conversation_area', 'deletions',
                'one_question_per_week', 'research',
                'starting_a_public_conversation', 'protected',
                'seasoned', 'spam']

    def location(self, item):
        return reverse(item)


class DonationsHelpSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['after_donating_to_a_candidate', 'donating_to_a_candidate',
                'donation_goals_citizen',
                'pledging_votes', 'campaign_contribution_rules',
                'quest_citizen']

    def location(self, item):
        return reverse(item)


class PoliciesHelpSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['advertising', 'be_nice',
                'do_not_spam',
                'feedback', 'finding_topics_of_interest',
                'how_to_search', 'markdown_formatting',
                'support', 'reporting_suspicious_behavior',
                'user_behavior', 'what_is_markdown']

    def location(self, item):
        return reverse(item)


class PrivilegeHelpSitemap(sitemaps.Sitemap):
    priority = 0.6
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['participate_in_the_conversation', 'upvote',
                'comment', 'flagging', 'downvote',
                'barista', 'tagging',
                'brewmaster', 'tribune']

    def location(self, item):
        return reverse(item)


class QuestHelpSitemap(sitemaps.Sitemap):
    priority = 0.6
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['donation_goals', 'funding_not_in_account',
                'how_to_export_contributions', 'how_to_get_on_the_ballot',
                'how_to_run',
                'name_on_ballot_to_run', 'need_more_help_repsagetribune',
                'principle_campaign_committee', 'quest_signup']

    def location(self, item):
        return reverse(item)


class QuestionHelpSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['context_to_a_question', 'duplicates',
                'quality_standards', 'questions_avoid_asking',
                'questions_no_longer_accepted',
                'solution_to_question', 'tags_and_how_to_use_them',
                'topics_to_ask_about', 'traffic_no_solutions']

    def location(self, item):
        return reverse(item)


class ReputationModerationHelpSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['admin_council', 'moderators',
                'reputation_changed_user_removed', 'serial_voting_change',
                'user_removed_change',
                'voting_importance', 'reputation']

    def location(self, item):
        return reverse(item)


class SecurityHelpSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['security_vulnerability']

    def location(self, item):
        return reverse(item)


class SolutionsHelpSitemap(sitemaps.Sitemap):
    priority = 0.4
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['good_solution', 'solution_to_own_question',
                'solutions_no_longer_accepted', 'when_to_edit_solutions',
                'why_are_solutions_removed']

    def location(self, item):
        return reverse(item)


class TermsHelpSitemap(sitemaps.Sitemap):
    priority = 0.3
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['trust_and_safety', 'terms_and_conditions',
                'quest_terms_and_conditions']

    def location(self, item):
        return reverse(item)
