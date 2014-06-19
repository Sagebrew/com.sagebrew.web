from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField


class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()


def upload_path(self, filename):
    return 'profile_pic/%s' % filename

class UserProfile(models.Model):
    avatar = models.ImageField(upload_to=upload_path,blank=True,null=True)

class CredentialsAdmin(admin.ModelAdmin):
    pass

class Client_Twitter(models.Model):
    #user = models.OneToOneField('Client')
    twitter_id = models.DecimalField(max_digits=20, decimal_places=0,null=True)
    access_token = models.CharField(max_length=200, null=True)
    access_token_secret = models.CharField(max_length=200, null=True)
    twitter_username = models.CharField(max_length=200, null=True)
    def __unicode__(self):
        return self.user.user.username

admin.site.register(CredentialsModel, CredentialsAdmin)