from datetime import datetime

from neomodel import CypherException, DoesNotExist
from rest_framework.reverse import reverse

from sb_base.decorators import apply_defense
from api.utils import request_to_api
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
    solution['upvotes'] = get_vote_count(solution['object_uuid'],
                                                1)
    solution['downvotes'] = get_vote_count(solution['object_uuid'],
                                                  0)
    solution['last_edited_on'] = datetime.strptime(
        solution['last_edited_on'][:len(solution['last_edited_on']) - 6],
        '%Y-%m-%d %H:%M:%S.%f')
    solution['created'] = datetime.strptime(
        solution['created'][:len(solution['created']) - 6],
        '%Y-%m-%d %H:%M:%S.%f')
    solution['vote_count'] = str(
        solution['upvotes'] - solution['downvotes'])
    url = reverse('solution-comments', kwargs={
        'object_uuid': solution['object_uuid']}, request=request)
    response = request_to_api(url, request.user.username, req_method="GET")
    solution["comments"] = response.json()

    return solution


def convert_dynamo_solutions(raw_solutions, request):
    solution_list = []
    for solution in raw_solutions:
        solution = convert_dynamo_solution(solution, request)
        vote_type = get_vote(solution['object_uuid'],
                                 request.user.username)
        if vote_type is not None:
            if vote_type['status'] == 2:
                vote_type = None
            else:
                vote_type = str(bool(vote_type['status'])).lower()
        solution['vote_type'] = vote_type
        solution_list.append(solution)
    return solution_list

