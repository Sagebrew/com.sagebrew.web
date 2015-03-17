from neomodel import CypherException, DoesNotExist

from sb_base.decorators import apply_defense

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
        solution = SBSolution.nodes.get(sb_id=solution_uuid)
    except (SBSolution.DoesNotExist, DoesNotExist):
        try:
            solution = SBSolution(content=content, sb_id=solution_uuid)
            solution.save()
        except CypherException as e:
            return e
    except CypherException as e:
        return e
    return solution

