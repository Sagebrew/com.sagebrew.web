from django.contrib.auth.backends import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework_auth0.authentication import Auth0JSONWebTokenAuthentication

from rest_framework_auth0.settings import auth0_api_settings, jwt_api_settings

jwt_decode_handler = jwt_api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = jwt_api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class Auth0JWT(Auth0JSONWebTokenAuthentication):
    """
    TODO:
        -- If created is true, go get the user from auth0 to make sure it's legit.
    """

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        UserModel = get_user_model()
        remote_user = jwt_get_username_from_payload(payload)

        if not remote_user:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)
            # RemoteUserBackend behavior:
            # return
        user = None
        username = self.clean_username(remote_user)

        if self.create_unknown_user:
            user, created = UserModel._default_manager.get_or_create(defaults={"provider": "auth0"}, **{
                UserModel.USERNAME_FIELD: username,
            })
            if created:
                user = self.configure_user(user)
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                msg = _('Invalid signature.')
                raise exceptions.AuthenticationFailed(msg)
                # RemoteUserBackend behavior:
                # pass
        user = self.configure_user_permissions(user, payload)
        return user if self.user_can_authenticate(user) else None

    def clean_username(self, username):
        """
        In the parent class, this replaces pipes with . However we've resolved this
        by allowing the char to be used.
        We'd need to 1) migrate data and two a) replace the . with a pipe prior to
        retrieving data from auth0.
        :param username:
        :return:
        """
        return username
