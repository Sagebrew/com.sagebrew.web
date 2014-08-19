import traceback
from operator import itemgetter

from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion

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
                    traceback.print_exc()
                    rel = pleb.object_weight.connect(question)
                    rel.weight = 20
                    rel.status = 'seen'
                    rel.save()
                    pleb.save()
                    question.save()
                except:
                    traceback.print_exc()
        elif item['type'] == 'pleb':
            if current_pleb == item['source']['pleb_email']:
                print 'here'
                search_results.remove(item)
            else:
                c_pleb = Pleb.index.get(email=current_pleb)
                pleb = Pleb.index.get(email=item['source']['pleb_email'])
                rel = c_pleb.user_weight.relationship(pleb)
                item['sb_score'] = rel.weight
        print item
    try:
        search_results = sorted(search_results, key=itemgetter('sb_score', 'score'),
                                reverse=True)
    except KeyError, e:
        print e
        traceback.print_exc()
        return False
    return search_results
