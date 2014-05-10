from django.contrib import admin
from .models import Profile

models = (Profile,)

admin.site.register(models)