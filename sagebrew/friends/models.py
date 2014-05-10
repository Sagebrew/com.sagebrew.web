from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver

from guardian.shortcuts import (assign, remove_perm)

from friends.signals import (friend_request_accepted,
                    friend_request_sent, friend_removed)
from notifications.models import (NOTIFICATION_MESSAGE,
                                               NOTIFICATIONS,
                                               Notification)


class FriendList(models.Model):
    owner = models.ForeignKey(User, null=True)
    pending_sent_list = models.ManyToManyField(User, null=True,
                                              related_name='pending_requests')
    pending_received_list = models.ManyToManyField(User, null=True,
                                          related_name='pending')
    user_list = models.ManyToManyField(User, null=True,
                                       related_name='accepted')

    def __unicode__(self):
        return "%s's Friend's List" % self.owner.username

    def accept_friend_request(self, friend):
        friends = friend.profile.friends

        self.pending_received_list.remove(friend)
        self.user_list.add(friend)
        friends.pending_sent_list.remove(self.owner)
        friends.user_list.add(self.owner)
        self.save()
        friend_request_accepted.send_robust(
                                sender=self.accept_friend_request.__name__,
                                user=self.owner,
                                friend=friend,
                                permission=assign)

    def decline_friend_request(self, friend):
        self.pending_received_list.remove(friend)
        friend.profile.friends.pending_sent_list.remove(self.owner)
        self.save()
        friend.save()

    def send_friend_request(self, friend):
        if((friend not in self.pending_sent_list.all()) and
                               (not self.is_friend(friend))):
            self.pending_sent_list.add(friend)
            friend.profile.friends.pending_received_list.add(self.owner)
            self.save()
            friend.save()
            friend_request_sent.send_robust(
                                sender=self.send_friend_request.__name__,
                                user=self.owner,
                                friend=friend)

    def remove_friend(self, friend):
        self.user_list.remove(friend)
        friend.profile.friends.user_list.remove(self.owner)
        self.save()
        friend.save()
        friend_removed.send_robust(sender=self.__class__,
                                           user=self.owner,
                                           friend=friend,
                                           permission=remove_perm)

    def is_friend(self, friend):
        if(friend in self.user_list.all()):
            return True
        else:
            return False

    def check_sent_pending(self, friend):
        if(User.objects.get(username=friend) in self.pending_sent_list.all()):
            return True
        else:
            return False

    def check_received_pending(self, friend):
        if(User.objects.get(username=friend) in
                            self.pending_received_list.all()):
            return True
        else:
            return False

    def get_friends_subset(self, friend_type):
        friend_subset = []
        for friend in self.user_list.all():
            if(friend.profile.user_type == friend_type):
                friend_subset.append(friend)
        return friend_subset


@receiver(friend_request_sent)
@receiver(friend_request_accepted)
def friend_request_notification(sender, **kw):
    notification_type, message = NOTIFICATIONS[sender]
    user = kw['user']
    friend = kw['friend']

    if(user.get_full_name()):
        message = NOTIFICATION_MESSAGE(user.get_full_name(), message)
    else:
        message = NOTIFICATION_MESSAGE(user.username, message)
    notification = Notification(owner=user,
                                message=message,
                                notification_type=notification_type)
    notification.save()
    friend.profile.notifications.add(notification)
    friend.save()
