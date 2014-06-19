from django.db import models


def upload_path(self, filename):
    return 'profile_pic/%s' % filename

class UserProfile(models.Model):
    avatar = models.ImageField(upload_to=upload_path,blank=True,null=True)

