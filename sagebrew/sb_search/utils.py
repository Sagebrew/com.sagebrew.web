import traceback
import logging
from operator import itemgetter

from api.utils import spawn_task
from .tasks import update_weight_relationship
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion

logger = logging.getLogger('loggly_logs')

def personalize_search_results(search_results, current_pleb):
    for item in search_results:
        if item['type'] == 'question':
            question = SBQuestion.index.get(question_id=item['source']['question_uuid'])
            pleb = Pleb.index.get(email=current_pleb)
            try:
                rel = pleb.object_weight.relationship(question)
                item['sb_score'] = rel.weight
            except (IndexError, KeyError):
                try:
                    spawn_task(task_func=update_weight_relationship, task_param={
                        'object_uuid': item['source']['question_uuid'],
                        'object_type': 'question',
                        'current_pleb': current_pleb,
                        'modifier_type': 'seen'
                    })
                except:
                    logger.excpetion("Unhandled exception, personalized search"
                                     "result")
                    traceback.print_exc()
        elif item['type'] == 'pleb':
            c_pleb = Pleb.index.get(email=current_pleb)
            pleb = Pleb.index.get(email=item['source']['pleb_email'])
            rel = c_pleb.user_weight.relationship(pleb)
            item['sb_score'] = rel.weight
        print item
    try:
        search_results = sorted(search_results, key=itemgetter('sb_score', 'score'),
                                reverse=True)
    except KeyError, e:
        traceback.print_exc()
        return False
    return search_results
