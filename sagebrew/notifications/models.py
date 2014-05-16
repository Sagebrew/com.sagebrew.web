from neo4django.db import models

from plebs.models import Pleb

class Notification(models.NodeModel):
    created = models.DateTimeProperty(auto_now=True)
    notify = models.Relationship(Pleb, rel_type='notifying')
    notifier = models.Relationship(Pleb, rel_type='notifier')
    message = models.StringProperty()
