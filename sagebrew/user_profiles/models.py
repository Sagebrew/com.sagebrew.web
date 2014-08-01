'''
Flying Frogs user profiles is the baseline profile for creating additional
elements to the base user class of django. If your app only needs additional
attributes added to one type of user profile then feel free to edit the profile
model here and set the USER_TYPES to "" and implement a simple create_profile
function that creates a profile based on your needed attributes.

If you need more than one type of user, create another app within your project
that is specific to your application. Then import the Profile model into
as many types of users as you need. All that is required is that you
define a tuple named USER_TYPES and import it into this file and create
a create_profile function that creates profiles for all of your types.
'''
from uuid import uuid1
import hashlib

from django.db import models
from django.contrib.auth.models import User

from model_utils.models import TimeStampedModel

from allauth.socialaccount.models import SocialAccount

# from plebs.models import Pleb

def user_unicode_patch(self):
    name = self.get_full_name()
    username = self.username
    return name or username


class Profile(TimeStampedModel):
    uuid = models.CharField(max_length=36, unique=True, blank=True, null=True,
                            verbose_name="UUID")
    User.__unicode__ = user_unicode_patch
    user = models.OneToOneField(User, verbose_name="Profile")

    def __unicode__(self):
        return "%s" % self.user.get_full_name()

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def save(self, *args, **kwargs):
        if (self.uuid == ""):
            self.uuid = str(uuid1())
        '''
        pleb = Pleb.objects.create(username=self.user.username,
                            name=self.user.get_full_name(), age=self.birthday,
                            primary_phone=self.primary_phone,
                            secondary_phone=self.secondary_phone,
                            user_quote=self.user_quote,
                            description=self.description,
                            profile_pic=self.profile_pic)
        pleb.save()
        '''
        super(Profile, self).save(*args, **kwargs)

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False

    def profile_image_url(self):
        fb_uid = SocialAccount.objects.filter(user_id=self.user.id,
                                              provider='facebook')

        if len(fb_uid):
            return "http://graph.facebook.com/{" \
                   "}/picture?width=40&height=40".format(
                fb_uid[0].uid)

        return "http://www.gravatar.com/avatar/{}?s=40".format(
            hashlib.md5(self.user.email).hexdigest())


User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])