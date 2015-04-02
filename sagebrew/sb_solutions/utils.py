from datetime import datetime

from django.template.loader import render_to_string

from neomodel import CypherException, DoesNotExist
from rest_framework.reverse import reverse

from api.utils import request_to_api
from sb_base.decorators import apply_defense
from sb_docstore.utils import get_vote_count, get_vote

from .neo_models import SBSolution


@apply_defense
def save_solution_util(content, solution_uuid):
    '''
    This util creates an solution and saves it, it then connects it to the
    question, and pleb

    :param content:
    :param current_pleb:
    :param solution_uuid:
    :param question_uuid:
    :return:
    '''
    try:
        solution = SBSolution.nodes.get(object_uuid=solution_uuid)
    except (SBSolution.DoesNotExist, DoesNotExist):
        try:
            solution = SBSolution(content=content, object_uuid=solution_uuid)
            solution.save()
        except CypherException as e:
            return e
    except CypherException as e:
        return e
    return solution


# TODO see if this can be replaced with convert_dynamo_content_with_comments
def convert_dynamo_solution(raw_solution, request):
    solution = dict(raw_solution)
    solution['upvotes'] = get_vote_count(solution['object_uuid'], 1)
    solution['downvotes'] = get_vote_count(solution['object_uuid'], 0)
    solution['last_edited_on'] = datetime.strptime(
        solution['last_edited_on'][:len(solution['last_edited_on']) - 6],
        '%Y-%m-%d %H:%M:%S.%f')
    solution['created'] = datetime.strptime(
        solution['created'][:len(solution['created']) - 6],
        '%Y-%m-%d %H:%M:%S.%f')
    solution['vote_count'] = str(solution['upvotes'] - solution['downvotes'])
    url = reverse('solution-comments', kwargs={
        'object_uuid': solution['object_uuid']}, request=request)
    response = request_to_api(url, request.user.username, req_method="GET")
    solution["comments"] = response.json()
    user_endpoint = reverse("user-detail",
                            kwargs={"username": solution["owner"]},
                            request=request)
    user_endpoint = "%s%s" % (user_endpoint, "?expand=True")
    response = request_to_api(user_endpoint, request.user.username,
                              req_method="GET")
    response_json = response.json()
    solution["profile"] = response_json["profile"]
    response_json.pop("profile", None)
    solution["owner_object"] = response_json

    return solution


def convert_dynamo_solutions(raw_solutions, request):
    solution_list = []
    raw_solutions = list(raw_solutions)
    for solution in raw_solutions:
        solution = convert_dynamo_solution(solution, request)
        vote_type = get_vote(solution['object_uuid'], request.user.username)
        if vote_type is not None:
            if vote_type['status'] == 2:
                vote_type = None
            else:
                vote_type = str(bool(vote_type['status'])).lower()
        solution['vote_type'] = vote_type
        solution_list.append(solution)
    return solution_list


def render_solutions(solution_dict):
    return render_to_string('solutions.html', solution_dict)