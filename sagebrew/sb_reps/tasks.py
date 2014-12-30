from celery import shared_task

from .utils import save_policy, save_experience
from .neo_models import Policy
from sb_docstore.tasks import add_object_to_table_task
from api.utils import spawn_task


@shared_task()
def save_policy_task(rep_id, category, description, object_uuid):
    res1 = save_policy(rep_id, category, description, object_uuid)
    if isinstance(res1, Exception):
        raise save_policy_task.retry(exc=res1, countdown=3, max_retries=None)
    task_data = {
        'table': 'policies',
        'object_data': {'parent_object': rep_id, 'object_uuid': object_uuid,
                        'category': category, 'description': description}
    }
    return True

@shared_task()
def save_experience_task(rep_id, title, start_date, end_date, current,
                         company, location, exp_id, description=""):
    experience = save_experience(rep_id, title, start_date, end_date, current,
                                 company, location, exp_id, description)
    if isinstance(experience, Exception):
        raise save_experience_task.retry(exc=experience, countdown=3,
                                         max_retries=None)
    return True