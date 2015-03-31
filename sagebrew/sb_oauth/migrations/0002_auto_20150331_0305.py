# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sb_oauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sbapplication',
            name='skip_authorization',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sbapplication',
            name='user',
            field=models.ForeignKey(related_name='sb_oauth_sbapplication', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
