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

from django.db import models
from django.contrib.auth.models import User
from django.http import Http404

from model_utils.models import TimeStampedModel

from localflavor.us.models import (PhoneNumberField)

from guardian.shortcuts import (assign)

from address.models import Address
from friends.models import FriendList
from notifications.models import Notification


def user_unicode_patch(self):
    name = self.get_full_name()
    username = self.username
    return name or username

class Profile(TimeStampedModel):
    uuid = models.CharField(max_length=36, unique=True, verbose_name="UUID")
    User.__unicode__ = user_unicode_patch
    user = models.OneToOneField(User, verbose_name="Pleb")
    lower_username = models.CharField(max_length=50, blank=True, null=True)
    address = models.ForeignKey(Address, blank=True)
    primary_phone = PhoneNumberField(blank=True)
    secondary_phone = PhoneNumberField(blank=True)
    notifications = models.ManyToManyField(Notification, blank=True,
                                            null=True)
    user_quote = models.CharField(max_length=64, blank=True)
    friends = models.ForeignKey(FriendList, blank=True, null=True,
                                related_name='friends_list')
    description = models.CharField(max_length=500, blank=True)
    profile_pic = models.URLField(max_length=1024)

    def __unicode__(self):
        return "%s" % self.user.get_full_name()

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        permissions = (
                        ('view_own_profile', 'View Own Profile'),
                        ('view_friend_profile', 'View Friend Profile'),
                        ('admin', 'Admin'),
                      )
    def save(self, *args, **kwargs):
        if(self.uuid == ""):
            self.uuid = str(uuid1())
        super(Profile, self).save(*args, **kwargs)


def create_profile(user, user_info, address, user_phone, user_type):
    '''
    Takes the information for a user and based on the passed type, decides
    which profile to store the information in. In the case of a failure
    the passed user is deleted because there is no need to keep the user
    if the profile is not created for him.
    '''
    try:
        profile = Profile(user=user, address=address,
                                  lower_username=user.username.lower(),
                                  primary_phone=user_phone,
                                  user_type=user_type)
        friends = FriendList(owner=user)
        friends.save()
        profile.friends = friends
        profile.save()
        assign('view_own_profile', user, user.profile)
    #  In production implement exception here that removes the user
    #  if the profile is unsuccessful in creating for some reason.
    except Exception as profile_fail:
        print str(profile_fail)
        # user.remove() Not doing anything...
        raise Http404
    return profile
