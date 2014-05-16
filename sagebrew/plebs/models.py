from neo4django.db import models

class Pleb(models.NodeModel):
    username = models.StringProperty()
    name = models.StringProperty()
    age = models.IntegerProperty()
    primary_phone = models.StringProperty()
    secondary_phone = models.StringProperty()
    user_quote = models.StringProperty()
    description = models.StringProperty()
    profile_pic = models.URLProperty()

    viewed_notification = models.Relationship(
                                'Notification', rel_type='viewed_notification')
    notifications = models.Relationship('Notification', rel_type='notifications')
    friends = models.Relationship('self',rel_type='friends_with')
    representatives = models.Relationship('self', rel_type='represented_by')
    address = models.Relationship('Address', rel_type='lives_at')
