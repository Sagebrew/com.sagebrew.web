from .neo_models import Round


def check_goal_completion_util(object_uuid=None):
    round_object = Round.nodes.get(object_uuid=object_uuid)
    return round_object.check_goal_completion()

