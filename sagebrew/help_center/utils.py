from sub_urls.account import urlpatterns as accounts
from sub_urls.asking import urlpatterns as asking
from sub_urls.citizens import urlpatterns as citizens
from sub_urls.conversation import urlpatterns as conversation
from sub_urls.policies import urlpatterns as policies
from sub_urls.privileges import urlpatterns as privileges
from sub_urls.representatives import urlpatterns as representatives
from sub_urls.reputation_and_moderation import (
    urlpatterns as reputation_and_moderation)
from sub_urls.security import urlpatterns as security
from sub_urls.solutions import urlpatterns as solutions
from sub_urls.terms import urlpatterns as terms

def populate_urls():
    urlpatterns = []
    for item in accounts:
        urlpatterns.append(item)
    for item in asking:
        urlpatterns.append(item)
    for item in citizens:
        urlpatterns.append(item)
    for item in conversation:
        urlpatterns.append(item)
    for item in policies:
        urlpatterns.append(item)
    for item in privileges:
        urlpatterns.append(item)
    for item in representatives:
        urlpatterns.append(item)
    for item in reputation_and_moderation:
        urlpatterns.append(item)
    for item in security:
        urlpatterns.append(item)
    for item in solutions:
        urlpatterns.append(item)
    for item in terms:
        urlpatterns.append(item)
    
    return urlpatterns