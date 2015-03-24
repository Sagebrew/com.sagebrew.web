from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated() is not True:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsSelfOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated() is not True:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsSelf(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated() is not True:
            return False

        return obj == request.user


class IsUserOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated() is not True:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated() is not True:
            return False

        return obj.user == request.user