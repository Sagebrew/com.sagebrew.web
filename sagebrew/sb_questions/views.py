from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.generic import View

from neomodel import DoesNotExist

from sb_registration.utils import verify_completed_registration
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
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def solution_edit_page(request, solution_uuid=None):
    data = {"object_uuid": solution_uuid}
    return render(request, 'edit_solution.html', data)


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class QuestionManagerView(LoginRequiredMixin):
    template_name = 'questions/save.html'

    @method_decorator(user_passes_test(
        verify_completed_registration,
        login_url='/registration/profile_information'))
    def dispatch(self, *args, **kwargs):
        return super(QuestionManagerView, self).dispatch(*args, **kwargs)

    def get(self, request, question_uuid=None, slug=None):
        if question_uuid is not None:
            try:
                question = Question.get(question_uuid)
            except (DoesNotExist, Question.DoesNotExist):
                return redirect('404_Error')
            return render(request, self.template_name, {
                'sort_by': 'uuid',
                'authors': question.get_conversation_authors(),
                'question': QuestionSerializerNeo(
                    question, context={"request": request}).data,
            })
        else:
            return render(request, self.template_name, {})
