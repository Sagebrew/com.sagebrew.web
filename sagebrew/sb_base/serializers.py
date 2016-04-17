import bleach
from intercom import Admin, Intercom

from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError

from neomodel import DoesNotExist

from api.serializers import SBSerializer
from api.utils import gather_request_data, render_content, spawn_task

from plebs.neo_models import Pleb

from .tasks import create_email, create_event


class VotableContentSerializer(SBSerializer):
    # TODO Deprecate in favor of id based on
    # http://jsonapi.org/format/#document-structure-resource-objects
    object_uuid = serializers.CharField(read_only=True)

    content = serializers.CharField()

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    # Need to figure out how we want to handle these user specific items
    # Maybe if no user is provided we just return None or don't include?
    vote_type = serializers.SerializerMethodField()

    view_count = serializers.SerializerMethodField()

    profile = serializers.SerializerMethodField()
    flagged = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    can_flag = serializers.SerializerMethodField()
    can_comment = serializers.SerializerMethodField()
    can_upvote = serializers.SerializerMethodField()
    can_downvote = serializers.SerializerMethodField()
    is_private = serializers.SerializerMethodField()
    html_content = serializers.SerializerMethodField()

    def get_profile(self, obj):
        from plebs.serializers import PlebSerializerNeo
        request, expand, _, relation, _ = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=self.context.get('expand_param', None))
        owner_username = obj.owner_username
        if expand == "true":
            owner = Pleb.get(username=owner_username)
            profile_dict = PlebSerializerNeo(
                owner, context={'request': request}).data
        elif relation == 'hyperlink':
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": owner_username},
                                   request=request)
        else:
            profile_dict = obj.owner_username
        return profile_dict

    def get_url(self, obj):
        """
        url provides a link to the human viewable page that the object appears
        on. This is for user consumption and templates.
        """
        request, _, _, _, _ = gather_request_data(self.context)
        if obj.url is None:
            try:
                return obj.get_url(request)
            except AttributeError:
                return None
        else:
            return obj.url

    def get_href(self, obj):
        """
        href provides a link to the objects API detail endpoint. This is for
        programmatic access.
        """
        request, _, _, _, _ = gather_request_data(self.context)
        if obj.href is None:
            try:
                return obj.get_href(request)
            except AttributeError:
                return None
        else:
            return obj.href

    def get_vote_count(self, obj):
        return obj.get_vote_count()

    def get_vote_type(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return obj.get_vote_type(request.user.username)

    def get_upvotes(self, obj):
        return obj.get_upvote_count()

    def get_downvotes(self, obj):
        return obj.get_downvote_count()

    def get_view_count(self, obj):
        return obj.get_view_count()

    def get_is_owner(self, obj):
        """
        Determine if the currently logged in user is the owner of this object.
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return False
        if not request.user.is_authenticated():
            return False
        return obj.owner_username == request.user.username

    def get_html_content(self, obj):
        if obj.content is not None:
            return bleach.clean(obj.content).replace('\n', "<br />")
        else:
            return None

    def get_can_comment(self, obj):
        """
        Determine if the currently logged in user can flag this object.
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        detail = None
        short_detail = None
        if request is None:
            return {"status": False,
                    "detail": "You must be logged in to comment on content.",
                    "short_detail": "Signup To Comment"}
        if not request.user.is_authenticated():
            return {"status": False,
                    "detail": "You must be logged in to comment on content.",
                    "short_detail": "Signup To Comment"}
        if obj.owner_username == request.user.username:
            # Always allow the owner to comment on their own content
            return {"status": True, "detail": detail,
                    "short_detail": short_detail}
        obj_type = obj.__class__.__name__.lower()
        if obj_type == "question" or obj_type == "solution":
            can_comment = "comment" in Pleb.get(
                username=request.user.username).get_privileges()
            if not can_comment:
                detail = "You must have 20+ reputation to comment on " \
                         "Conversation Cloud content."
                short_detail = "Requirement: 20+ Reputation"
        else:
            can_comment = True

        return {"status": can_comment, "detail": detail,
                "short_detail": short_detail}

    def get_can_flag(self, obj):
        """
        Determine if the currently logged in user can flag this object.
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        detail = None
        short_detail = None
        if request is None:
            return {"status": False,
                    "detail": "You must be logged in to flag content.",
                    "short_detail": "Signup To Flag"}
        if not request.user.is_authenticated():
            return {"status": False,
                    "detail": "You must be logged in to flag content.",
                    "short_detail": "Signup To Flag"}
        if obj.owner_username == request.user.username:
            return {"status": False,
                    "detail": "You cannot flag your own content",
                    "short_detail": "Cannot Flag Own Content"}
        obj_type = obj.__class__.__name__.lower()
        if obj_type == "question" or obj_type == "solution":
            can_flag = "flag" in Pleb.get(
                username=request.user.username).get_privileges()
            if not can_flag:
                detail = "You must have 50+ reputation to flag Conversation " \
                         "Cloud content."
                short_detail = "Requirement: 50+ Reputation"
        elif obj_type == "comment" and hasattr(obj, 'parent_type') and \
                (obj.parent_type == "question" or obj_type == "solution"):
            can_flag = "flag" in Pleb.get(
                username=request.user.username).get_privileges()
            if not can_flag:
                detail = "You must have 50+ reputation to flag Conversation " \
                         "Cloud content."
                short_detail = "Requirement: 50+ Reputation"
        else:
            can_flag = True

        return {"status": can_flag, "detail": detail,
                "short_detail": short_detail}

    def get_flagged(self, obj):
        """
        Determine if the currently logged in user has already flagged this
        object
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return False
        if not request.user.is_authenticated():
            return False

        return request.user.username in obj.get_flagged_by()

    def get_can_upvote(self, obj):
        """
        Determine if the currently logged in user can up vote this object.
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        can_upvote = True
        detail = None
        short_detail = None
        if request is None:
            return {"status": False,
                    "detail": "You must be logged in to upvote content.",
                    "short_detail": "Signup To Vote"}
        if not request.user.is_authenticated():
            return {"status": False,
                    "detail": "You must be logged in to upvote content.",
                    "short_detail": "Signup To Vote"}
        obj_type = obj.__class__.__name__.lower()
        # Duplicated logic for sake of readability
        if obj_type == "question" or obj_type == "solution":
            if obj.owner_username == request.user.username:
                can_upvote = False
                detail = "You cannot upvote your own " \
                         "Conversation Cloud content"
                short_detail = "Cannot Upvote Own " \
                               "Conversation Cloud Content"
        elif obj_type == "comment" and hasattr(obj, 'parent_type') and \
            (obj.parent_type == "question" or
                obj.parent_type == "solution"):
            if obj.owner_username == request.user.username:
                can_upvote = False
                detail = "You cannot upvote your own " \
                         "Conversation Cloud content"
                short_detail = "Cannot Upvote Own " \
                               "Conversation Cloud Content"

        # Currently we allow everyone to upvote without regulation. This is
        # to generate an initial base of reputation.

        return {"status": can_upvote, "detail": detail,
                "short_detail": short_detail}

    def get_can_downvote(self, obj):
        """
        Determine if the currently logged in user can down vote this object.
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        detail = None
        short_detail = None
        can_downvote = False
        if request is None:
            return {"status": False,
                    "detail": "You must be logged in to downvote content.",
                    "short_detail": "Signup To Vote"}
        if not request.user.is_authenticated():
            return {"status": False,
                    "detail": "You must be logged in to downvote content.",
                    "short_detail": "Signup To Vote"}
        obj_type = obj.__class__.__name__.lower()
        if obj_type == "question" or obj_type == "solution":
            can_downvote = "downvote" in Pleb.get(
                username=request.user.username).get_privileges()
            if obj.owner_username == request.user.username:
                can_downvote = False
                detail = "You cannot downvote your own " \
                         "Conversation Cloud content"
                short_detail = "Cannot Downvote Own " \
                               "Conversation Cloud Content"
            elif not can_downvote:
                can_downvote = False
                detail = "You must have 100+ reputation to downvote" \
                         " Conversation Cloud content."
                short_detail = "Requirement: 100+ Reputation"
        elif obj_type == "comment" and hasattr(obj, 'parent_type') and \
                (obj.parent_type == "question" or
                    obj.parent_type == "solution"):
            if obj.owner_username == request.user.username:
                can_downvote = False
                detail = "You cannot downvote your own " \
                         "Conversation Cloud content"
                short_detail = "Cannot Downvote Own " \
                               "Conversation Cloud Content"
            elif "downvote" not in Pleb.get(
                    username=request.user.username).get_privileges():
                can_downvote = False
                detail = "You must have 100+ reputation to downvote" \
                         " Conversation Cloud content."
                short_detail = "Requirement: 100+ Reputation"
        else:
            can_downvote = True

        return {"status": can_downvote, "detail": detail,
                "short_detail": short_detail}

    def get_is_private(self, obj):
        obj_type = obj.__class__.__name__.lower()
        if obj_type == "question" or obj_type == "solution":
            return False
        elif obj_type == "comment" and hasattr(obj, 'parent_type') and \
                (obj.parent_type == "question" or
                    obj.parent_type == "solution"):
            return False
        elif obj_type == "post":
            return True
        elif obj_type == "comment" and hasattr(obj, 'parent_type') and \
                obj.parent_type == "post":
            return True
        else:
            return False


class ContentSerializer(VotableContentSerializer):
    last_edited_on = serializers.DateTimeField(read_only=True)
    # Need to figure out how we want to handle these user specific items
    # Maybe if no user is provided we just return None or don't include?
    to_be_deleted = serializers.BooleanField(read_only=True)
    flagged_by = serializers.SerializerMethodField()
    council_vote = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField(read_only=True)

    def get_flagged_by(self, obj):
        return obj.get_flagged_by()

    def get_council_vote(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        return obj.get_council_vote(request.user.username)


class MarkdownContentSerializer(ContentSerializer):
    html_content = serializers.SerializerMethodField()

    def get_html_content(self, obj):
        return render_content(obj.content, obj.object_uuid)


class TitledContentSerializer(MarkdownContentSerializer):
    title = serializers.CharField(required=False,
                                  min_length=15, max_length=140)


def validate_is_owner(request, instance):
    if request is None:
        raise serializers.ValidationError("Cannot update without request")
    if instance.owner_username is not None:
        if instance.owner_username != request.user.username:
            raise serializers.ValidationError("Only the owner can edit this")
    return True


def validate_to_or_from(value):
    Intercom.app_id = settings.INTERCOM_APP_ID
    Intercom.app_api_key = settings.INTERCOM_API_KEY
    value_type = value.get('type', None)
    user_id = value.get('user_id', None)
    passed_id = value.get('id', None)
    if value_type != "user" and value_type != "admin":
        raise serializers.ValidationError("The only valid values for 'type' "
                                          "are 'user' and 'admin'")
    if value_type == "user" and user_id is None:
        raise serializers.ValidationError("Must provide the 'user_id' key "
                                          "when attempting to send a message "
                                          "to or from a user")
    if value_type == "admin":
        if passed_id is None:
            raise serializers.ValidationError("Must provide the 'id' key when "
                                              "attempting to send a message "
                                              "to or from an admin")

        if str(passed_id) not in [admin.id for admin in Admin.all()]:
            raise serializers.ValidationError(
                "%s is not a valid admin ID" % passed_id)
    try:
        Pleb.get(username=user_id)
    except (Pleb.DoesNotExist, DoesNotExist):
        if value_type != 'admin':
            raise serializers.ValidationError(
                "Profile %s Does Not Exist" % user_id)

    return value


class IntercomMessageSerializer(serializers.Serializer):
    message_type = serializers.CharField()
    subject = serializers.CharField()
    body = serializers.CharField()
    template = serializers.ChoiceField(choices=[
        ('plain', 'plain'), ('personal', 'personal'),
        ('company', 'company'), ('announcement', 'announcement')
    ])
    from_user = serializers.DictField(child=serializers.CharField(),
                                      validators=[validate_to_or_from])
    to_user = serializers.DictField(child=serializers.CharField(),
                                    validators=[validate_to_or_from])

    def create(self, validated_data):
        from_user = validated_data.pop('from_user', None)
        to_user = validated_data.pop('to_user', None)
        validated_data['from'] = from_user
        validated_data['to'] = to_user
        spawn_task(task_func=create_email, task_param=validated_data)
        validated_data['from_user'] = from_user
        validated_data['to_user'] = to_user
        return validated_data


class IntercomEventSerializer(serializers.Serializer):
    # TODO once we have 120 event_names defined we'll want to make sure the
    # event name exists within the list and does not go over the limit.
    event_name = serializers.CharField()
    username = serializers.CharField()
    metadata = serializers.DictField(required=False)

    def validate_username(self, value):
        try:
            Pleb.get(username=value)
        except(DoesNotExist, Exception):
            raise ValidationError('Does not exist in the database.')

        return value

    def create(self, validated_data):
        spawn_task(task_func=create_event, task_param=validated_data)
        return validated_data
