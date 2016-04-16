from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic import View

from neomodel import DoesNotExist, db

from sb_questions.neo_models import Question

from .serializers import QuestionSerializerNeo


def question_page(request, sort_by="most_recent"):
    """
    This is the page that displays what is returned from the get_question_view
    api endpoint

    Only pass 'question_uuid' parameter if you want to get a single question
    that matched the uuid. This will most likely occur when clicking on a
    question which is shown on your newsfeed or another page

    :param sort_by:
    :param request:

                request.data/request.body = {
                    'question_uuid': str(uuid1()),
                    'current_pleb': 'example@email.com'
                    'sort_by': ''
                }

    :return:
    """
    return render(
        request, 'questions/list.html',
        {
            "base_tags": [{'default': tag, 'display': tag.replace('_', ' ')}
                          for tag in settings.BASE_TAGS]
        }
    )


def question_redirect_page(request, question_uuid):
    """
    This is the view that displays a single question with all solutions,
    comments,
    references and tags.

    :param question_uuid:
    :param request:
    :return:
    """

    return redirect(
        "question_detail_page", question_uuid=question_uuid,
        slug=slugify(Question.get(object_uuid=question_uuid).title),
        permanent=True)


@login_required()
def solution_edit_page(request, solution_uuid=None):
    """
    This is in the questions views for right now due to ease of url structuring.
    We can move it to solutions.views but that will require some changing for
    the single page setup.
    """
    query = 'MATCH (a:Solution {object_uuid: "%s"}) ' \
            'RETURN CASE '\
            'WHEN a.owner_username = "%s" THEN TRUE ' \
            'ELSE FALSE END' % (solution_uuid, request.user.username)
    res, _ = db.cypher_query(query)
    if res.one is False:
        return redirect('401_Error')
    return render(request, 'solutions/edit.html',
                  {"object_uuid": solution_uuid})


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        if initkwargs.get('template_name') == "conversation.html":
            return view
        return login_required(view)


class QuestionManagerView(LoginRequiredMixin):
    template_name = 'questions/save.html'

    def get(self, request, question_uuid=None, slug=None):
        if question_uuid is not None:
            try:
                question = Question.get(question_uuid)
            except (DoesNotExist, Question.DoesNotExist):
                return redirect('404_Error')
            if question.owner_username != request.user.username \
                    and self.template_name == "questions/edit.html":
                return redirect('401_Error')
            return render(request, self.template_name, {
                'sort_by': 'uuid',
                'authors': question.get_conversation_authors(),
                'question': QuestionSerializerNeo(
                    question, context={"request": request}).data,
            })
        else:
            return render(request, self.template_name, {})
