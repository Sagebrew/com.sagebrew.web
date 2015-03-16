from django.conf.urls import patterns, url

from .views import (save_solution_view)

urlpatterns = patterns(
    'sb_solutions.views',
    url(r'^submit_solution_api/$', save_solution_view, name="save_solution"),
)