from uuid import uuid1

from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from sb_docstore.utils import add_object_to_table, get_rep_docs, update_doc
from sb_docstore.tasks import build_rep_page_task
from sb_registration.utils import (verify_completed_registration)

from .forms import (EducationForm, ExperienceForm, PolicyForm, BioForm,
                    GoalForm)
from .neo_models import BaseOfficial
from .tasks import (save_policy_task, save_experience_task,
                    save_education_task, save_bio_task, save_goal_task)
from .utils import get_rep_type



@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def saga(request, username):
    representative = {"username": username}
    return render(request, 'action_page.html',
                  {"representative": representative,
                   "registered": False})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def updates(request, username):
    representative = {"username": username}
    return render(request, 'action_page.html',
                  {"representative": representative,
                   "registered": False})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def about(request, username):
    representative = {"username": username}
    return render(request, 'action_page.html',
                  {"representative": representative, "registered": False})

@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def representative_page(request, rep_type="", rep_id=""):
    res = get_rep_docs(rep_id, True)
    if isinstance(res, Exception):
        return redirect('404_Error')
    if not res:
        spawn_task(build_rep_page_task, {"rep_id": rep_id})
        try:
            temp_type = get_rep_type(dict(settings.BASE_REP_TYPES)[rep_type])
            official = temp_type.nodes.get(object_uuid=rep_id)
        except (temp_type.DoesNotExist, DoesNotExist, CypherException):
            return redirect('profile_page', request.user.username)
        pleb = official.pleb.all()[0]
        name = pleb.first_name+' '+pleb.last_name
        full = official.title+pleb.first_name+' '+pleb.last_name
        username = pleb.username
        data = {
            "name": name,
            "full": full, "username": username,
            "rep_id": rep_id, 'bio': official.bio
        }
        return render(request, 'rep_page.html', data)
    data = {
        'name': res['name'], 'full': res['full'],
        'username': res['username'], 'rep_id': res['rep_id'],
        'bio': res['bio']
    }
    return render(request, 'rep_page.html', data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_rep_info(request):
    rep_id =  str(request.DATA['rep_id'])
    res = get_rep_docs(rep_id)
    if isinstance(res, Exception):
        return redirect('404_Error')
    if not res:
        policy_list = []
        experience_list = []
        education_list = []
        goal_list = []
        spawn_task(build_rep_page_task, {"rep_id": rep_id})
        try:
            official = BaseOfficial.nodes.get(object_uuid=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException):
            return redirect('profile_page', request.user.username)
        policies = official.policy.all()
        experiences = official.experience.all()
        education = official.education.all()
        goals = official.goal.all()
        for goal in goals:
            goal_list.append(goal.get_dict())
        for policy in policies:
            policy_list.append(policy.get_dict())
        for experience in experiences:
            experience_list.append(experience.get_dict())
        for edu in education:
            education_list.append(edu.get_dict())
        policy_html = render_to_string('policy_list.html',
                                       {'policies': policy_list})
        experience_html = render_to_string('experience_list.html',
                                           {'experiences': experience_list})
        education_html = render_to_string('education_list.html',
                                          {'educations': education_list})
        goals_html = render_to_string('goal_list.html', {'goals': goal_list})
    else:
        policies = res['policies']
        experiences = res['experiences']
        education = res['education']
        goals = res['goals']
        policy_html = render_to_string('policy_list.html',
                                       {'policies': policies})
        experience_html = render_to_string('experience_list.html',
                                           {'experiences': experiences})
        education_html = render_to_string('education_list.html',
                                          {'educations': education})
        goals_html = render_to_string('goal_list.html', {'goals': goals})
    return Response({"policy_html": policy_html,
                     "experience_html": experience_html,
                     "education_html": education_html,
                     "goal_html": goals_html}, 200)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def get_experience_form(request):
    experience_form = ExperienceForm(request.DATA or None)
    if request.method == 'POST':
        if experience_form.is_valid():
            rep_id = str(request.DATA['rep_id'])
            uuid = str(uuid1())
            data = {'rep_id': rep_id,
                    'title': experience_form.cleaned_data['title'],
                    'start_date': experience_form.cleaned_data['start_date'],
                    'end_date': experience_form.cleaned_data['end_date'],
                    'current': experience_form.cleaned_data['current'],
                    'company': experience_form.cleaned_data['company'],
                    'location': experience_form.cleaned_data['location'],
                    'description': experience_form.cleaned_data['description'],
                    'exp_id': uuid}
            table_data = {'parent_object': rep_id,
                    'title': experience_form.cleaned_data['title'],
                    'start_date': unicode(
                        experience_form.cleaned_data['start_date']),
                    'end_date': unicode(
                        experience_form.cleaned_data['end_date']),
                    'current': experience_form.cleaned_data['current'],
                    'company': experience_form.cleaned_data['company'],
                    'location': experience_form.cleaned_data['location'],
                    'description': experience_form.cleaned_data['description'],
                    'object_uuid': uuid}
            res = add_object_to_table('experiences', table_data)
            if isinstance(res, Exception):
                return Response({"detail": "error1"}, 400)
            res = spawn_task(save_experience_task, data)
            if isinstance(res, Exception):
                return Response({"detail": "error2"}, 400)
            rendered = render_to_string('experience_detail.html',
                                        {'experience': data})
            return Response({"detail": "success",
                             "rendered": rendered}, 200)
        else:
            return Response({"detail": "invalid form"}, 400)
    else:
        rendered = render_to_string('experience_form.html',
                                    {'experience_form': experience_form})
        return Response({"rendered": rendered}, 200)


@api_view(['GET','POST'])
@permission_classes((IsAuthenticated,))
def get_policy_form(request):
    policy_form = PolicyForm(request.DATA or None)
    if request.method == "POST":
        if policy_form.is_valid():
            rep_id = request.DATA['rep_id']
            data = {
                'rep_id': rep_id,
                'category': policy_form.cleaned_data['policies'],
                'description': policy_form.cleaned_data['description'],
                'object_uuid': str(uuid1())
            }
            res = spawn_task(save_policy_task, data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            data['parent_object'] = str(rep_id)
            res = add_object_to_table('policies', data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            rendered = render_to_string('policy_detail.html', {'policy': data})
            return Response({"detail": "success",
                             "rendered": rendered}, 200)
    else:
        rendered = render_to_string('policy_form.html',
                          {'policy_form': policy_form})
        return Response({"rendered": rendered}, 200)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def get_education_form(request):
    education_form = EducationForm(request.DATA or None)
    if request.method == "POST":
        if education_form.is_valid():
            rep_id = str(request.DATA['rep_id'])
            uuid = str(uuid1())
            data = {
                'rep_id': rep_id,
                'school': education_form.cleaned_data['school'],
                'start_date': education_form.cleaned_data['start_date'],
                'end_date': education_form.cleaned_data['end_date'],
                'degree': education_form.cleaned_data['degree'],
                'edu_id': uuid
            }
            res = spawn_task(save_education_task, data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)

            data = {
                'parent_object': rep_id,
                'school': education_form.cleaned_data['school'],
                'start_date': unicode(
                    education_form.cleaned_data['start_date']),
                'end_date': unicode(education_form.cleaned_data['end_date']),
                'degree': education_form.cleaned_data['degree'],
                'object_uuid': uuid
            }
            res = add_object_to_table('education', data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            rendered = render_to_string('education_detail.html',
                                        {'education': data})
            return Response({"rendered": rendered}, 200)
    else:
        rendered = render_to_string('education_form.html',
                                    {'education_form': education_form})
        return Response({'rendered': rendered}, 200)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def get_bio_form(request):
    bio_form = BioForm(request.DATA or None)
    if request.method == 'POST':
        if bio_form.is_valid():
            rep_id = str(request.DATA['rep_id'])
            data = {
                "rep_id": rep_id,
                "bio": bio_form.cleaned_data['bio']
            }
            res = spawn_task(save_bio_task, data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            update_data = [{'update_key': 'bio',
                            'update_value': bio_form.cleaned_data['bio']}]
            res = update_doc('general_reps', rep_id, update_data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            rendered = render_to_string('bio_detail.html',
                                        {'bio': bio_form.cleaned_data['bio']})
            return Response({'rendered': rendered}, 200)
    else:
        rendered = render_to_string('bio_form.html', {'bio_form': bio_form})
        return Response({"rendered": rendered}, 200)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def get_goal_form(request):
    goal_form = GoalForm(request.DATA or None)
    if request.method == "POST":
        if goal_form.is_valid():
            rep_id = str(request.DATA['rep_id'])
            uuid = str(uuid1())
            data = {
                "rep_id": rep_id,
                "vote_req": goal_form.cleaned_data['vote_req'],
                "money_req": goal_form.cleaned_data['money_req'],
                "initial": goal_form.cleaned_data['initial'],
                "description": goal_form.cleaned_data['description'],
                "goal_id": uuid
            }
            res = spawn_task(save_goal_task, data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            data['parent_object'] = data['rep_id']
            data['object_uuid'] = data['goal_id']
            res = add_object_to_table('goals', data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            rendered = render_to_string('goal_detail.html',
                                        {'goal': data})
            return Response({'rendered': rendered}, 200)
        else:
            return Response({"detail": goal_form.errors}, 400)
    else:
        rendered = render_to_string('goal_form.html', {'goal_form': goal_form})
        return Response({"rendered": rendered}, 200)