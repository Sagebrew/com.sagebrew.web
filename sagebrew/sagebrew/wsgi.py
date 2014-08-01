"""
WSGI config for sagebrew project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sagebrew.settings")
os.environ.setdefault("BOMBERMAN_API_KEY", "6a224aea0ecb3601ae9197c5762aef56")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
