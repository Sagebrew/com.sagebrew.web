from django.contrib.auth.models import User

class ProxyUser(User):
    class Meta:
        proxy = True
        permissions = (
            ("has_registered", "Can use the full site")
        )