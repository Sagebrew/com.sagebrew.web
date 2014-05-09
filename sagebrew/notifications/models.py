from django.db import models
from django.contrib.auth.models import User
# Create your models here.
NOTIFICATIONS = {
                        'send_friend_request': ['Friend Request',
                                                ("has sent you a friend" +
                                                " request")],
                        'wall_post': 'Wall Post',
                        'response': 'Response',
                        'accept_friend_request': ['Friend Request Accepted',
                                                   "has accepted your \
                                                   friend request"],
                        'message': 'Message',
                     }

NOTIFICATION_MESSAGE = lambda name, message: '%s ' % (name) + message


class Notification(models.Model):
    time_stamp = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, null=True, related_name='owner')
    message = models.CharField(max_length=1024)
    # This is set internally so choices is not used because we do not
    # need to restrict the user and by using a dict instead of tuple
    # we are able to improve the readability and portability of our
    # functions that use the notification type. If there is an easy
    # way to use the tuple to access the information in it via a
    # string argument such as mytuple("key_value") then we should
    # switch back.
    notification_type = models.CharField(max_length=30, blank=True)
    viewed = models.BooleanField()

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-time_stamp']

    def __unicode__(self):
        return "%s's %d Message" % (self.owner.username, self.id)

    def notification_viewed(self):
        self.viewed = True
        self.save()
