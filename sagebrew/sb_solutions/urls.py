from django.conf.urls import patterns, url

from .views import (save_solution_view, edit_solution_view)

urlpatterns = patterns(
    'sb_solutions.views',
    url(r'^submit_solution_api/$', save_solution_view, name="save_solution"),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<solution_uuid>[A-Za-z0-9.@_%+-]{36})/edit/$', edit_solution_view,
        name='edit_solution_page'),
)