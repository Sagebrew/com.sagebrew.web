from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from neomodel import DoesNotExist, db

from sagebrew.sb_questions.neo_models import Question

from .serializers import QuestionSerializerNeo


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
    if res[0] if res else None is False:
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
                'solution_placeholder': render_to_string(
                    "solutions/placeholder.html"),
                'question': QuestionSerializerNeo(
                    question, context={"request": request}).data,
            })
        else:
            return render(request, self.template_name, {
                'question_placeholder': render_to_string(
                    'questions/placeholder.html')
            })
