import markdown

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.serializers import SBSerializer
from api.utils import gather_request_data

from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb


def replace_images(end_temp, content, identifier):
    # Get the beginning of the image tag to the end of the document
    image = end_temp.find('<img ')
    if image == -1:
        return content
    temp_content = end_temp[image:]
    # Set the remaining string to parse to the end of the current image tag
    end_temp = temp_content[temp_content.find("/>") + 2:]
    # Chop off the rest of the document after the close of the img
    # tag
    temp_content = temp_content[:temp_content.find("/>") + 2]
    # Need to get the source of the image to populate the a href
    # so find the src and chop off anything before it
    src = temp_content[temp_content.find('src="') + 5:]
    # Chop off anything after it is closed
    src = src[:src.find('"')]
    # Build the wrapper
    lightbox_wrapper = '<a href="%s" data-lightbox="%s">%s</a>' % (
        src, identifier, temp_content)
    # Replace the instances of the image tag with the new wrapper
    content = content.replace(temp_content, lightbox_wrapper, 1)
    if end_temp.find('<img ') != -1:
        return replace_images(end_temp, content, identifier)
    return content


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

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    can_flag = serializers.SerializerMethodField()
    can_comment = serializers.SerializerMethodField()
    html_content = serializers.SerializerMethodField()

    def get_profile(self, obj):
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
        if hasattr(obj, 'owner_username'):
            return obj.owner_username == request.user.username
        else:
            return False

    def get_html_content(self, obj):
        return obj.content.replace('\n', "<br />")

    def get_can_comment(self, obj):
        """
        Determine if the currently logged in user can flag this object.
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        detail = None
        if request is None:
            can_flag = False
            detail = "You must be logged in to comment on content."
        if not request.user.is_authenticated():
            can_flag = False
            detail = "You must be logged in to comment on content."
        obj_type = obj.__class__.__name__.lower()
        if obj_type == "question" or obj_type == "solution":
            can_flag = "flag" in Pleb.get(
                username=request.user.username).get_privileges()
            if not can_flag:
                detail = "You currently don't have the privilege required to " \
                         "comment on Conversation Cloud content."
        elif obj_type == "comment" and hasattr(obj, 'parent_type') and \
                (obj.parent_type == "question" or obj_type == "solution"):
            can_flag = "flag" in Pleb.get(
                username=request.user.username).get_privileges()
            detail = "Commenting on Conversation Cloud content requires "
        else:
            can_flag = True

        return {"status": can_flag, "detail": detail}

    def get_can_flag(self, obj):
        """
        Determine if the currently logged in user can flag this object.
        :param obj:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        detail = None
        if request is None:
            can_flag = False
            detail = "You must be logged in to flag content."
        if not request.user.is_authenticated():
            can_flag = False
            detail = "You must be logged in to flag content."
        obj_type = obj.__class__.__name__.lower()
        if obj_type == "question" or obj_type == "solution":
            can_flag = "flag" in Pleb.get(
                username=request.user.username).get_privileges()
            if not can_flag:
                detail = "You currently don't have the privilege required to " \
                         "flag Conversation Cloud content."
        elif obj_type == "comment" and hasattr(obj, 'parent_type') and \
                (obj.parent_type == "question" or obj_type == "solution"):
            can_flag = "flag" in Pleb.get(
                username=request.user.username).get_privileges()
            detail = "You currently don't have the privilege required to " \
                     "flag Conversation Cloud content."
        else:
            can_flag = True

        return {"status": can_flag, "detail": detail}

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
        if obj.content is not None:
            content = markdown.markdown(obj.content.replace(
                '&gt;', '>')).replace('<a', '<a target="_blank"')
            # Iterate through each image tag within the document and add the
            # necessary a tag for lightbox to work.
            return replace_images(content, content, obj.object_uuid)
        else:
            return ""


class TitledContentSerializer(MarkdownContentSerializer):
    title = serializers.CharField(required=False,
                                  min_length=15, max_length=140)
