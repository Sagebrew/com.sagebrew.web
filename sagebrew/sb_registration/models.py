from datetime import date
from django.conf import settings
from django.utils.http import int_to_base36, base36_to_int
from django.utils.crypto import constant_time_compare, salted_hmac


class EmailAuthTokenGenerator(object):
    '''
    This object is created for user email verification
    '''

    def make_token(self, user, pleb):
        if pleb is None:
            return None
        return self._make_timestamp_token(user, self._num_days(self._today()),
                                          pleb)

    def check_token(self, user, token, pleb):
        if token is None:
            return False
        try:
            timestamp_base36, hash_key = token.split("-")
        except ValueError:
            return False

        try:
            timestamp = base36_to_int(timestamp_base36)
        except ValueError:
            return False

        if not constant_time_compare(self._make_timestamp_token(
                user, timestamp, pleb), token):
            return False

        if (self._num_days(self._today()) - timestamp) > \
                settings.EMAIL_VERIFICATION_TIMEOUT_DAYS:
            return False

        return True

    def _make_timestamp_token(self, user, timestamp, pleb):
        timestamp_base36 = int_to_base36(timestamp)

        key_salt = "sagebrew.sb_registration.models.EmailAuthTokenGenerator"
        hash_val = "%s%s%s%s%s" % (user.username, user.first_name,
                                   user.last_name, user.email,
                                   pleb.email_verified)

        created_hash = salted_hmac(key_salt, hash_val).hexdigest()[::2]
        return "%s-%s" % (timestamp_base36, created_hash)

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        return date.today()

token_gen = EmailAuthTokenGenerator()
