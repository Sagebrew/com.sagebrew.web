from django.conf.urls import patterns, url

from .views import (QuestionManagerView,
                    question_page, solution_edit_page,
                    question_redirect_page)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^$', question_page, name='question_page'),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/$', question_redirect_page,
        name='question_redirect_page'),
    url(r'^solutions/(?P<solution_uuid>[A-Za-z0-9.@_%+-]{36})/edit/$',
        solution_edit_page, name='solution-edit'),
    url(r'^submit_question/$',
        QuestionManagerView.as_view(template_name='questions/create.html'),
        name="question-create"),
    url(r'^questions/(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/edit/$',
        QuestionManagerView.as_view(template_name='questions/edit.html'),
        name="question-edit"),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/$',
        QuestionManagerView.as_view(template_name='conversation.html'),
        name="question_detail_page"),
)
