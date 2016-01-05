from django.conf.urls import patterns, url

from .views import (submit_question_view_page, question_edit_page,
                    question_page, question_detail_page, solution_edit_page,
                    question_redirect_page)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^$', question_page, name='question_page'),
    url(r'^submit_question/$', submit_question_view_page,
        name='save_question_page'),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/$', question_redirect_page,
        name='question_redirect_page'),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/$',
        question_detail_page,
        name='question_detail_page'),
    url(r'^solutions/(?P<solution_uuid>[A-Za-z0-9.@_%+-]{36})/edit/$',
        solution_edit_page, name='solution-edit'),
    url(r'^questions/(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/edit/$',
        question_edit_page, name='question-edit')
)
