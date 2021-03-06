from rest_framework import permissions

from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission


class IsOwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if (obj.owner_username == request.user.username or
                request.user.is_staff):
            return True
        else:
            return False


class IsSelfOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.username == request.user.username


class IsAnonCreateReadOnlyOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == "POST" and not request.user.is_authenticated():
            return True
        elif not request.user.is_authenticated() and request.method != "POST":
            return False
        elif request.method in permissions.SAFE_METHODS:
            return True

        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated():
            return False
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.username == request.user.username


class IsUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user or request.user.is_staff:
            return True
        else:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class IsOwnerOrModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.username in \
                Quest.get_moderators(obj.owner_username) or \
                request.user.username == obj.owner_username:
            # Only allow the owner of the quest delete it
            if request.method == 'DELETE' and \
                    request.user.username != obj.owner_username:
                return False
            return True
        else:
            return False


class IsOwnerOrModerator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.username in \
                Quest.get_moderators(owner_username=obj) or \
                request.user.username == obj or request.user.username in \
                Mission.get_moderators(owner_username=obj):
            return True
        else:
            return False


class IsOwnerOrEditor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.username in Quest.get_editors(obj) or \
                request.user.username == obj:
            return True
        else:
            return False
