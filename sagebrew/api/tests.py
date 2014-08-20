# Create your tests here.
res = {
{u'users': [{u'num': 1}, {u'user_relationships': [
    {u'user_last_name': u'Wiersing', u'user_first_name': u'Tyler',
     u'user_full_name': u'Tyler Wiersing',
     u'user_email': u'tyler.wiersing@gmail.com'},
    {u'user_last_name': u'Wiersing', u'user_first_name': u'Tyler',
     u'user_full_name': u'Tyler Wiersing',
     u'user_email': u'tyler.wiersing1@gmail.com'},
    {u'user_last_name': u'Bleibtrey', u'user_first_name': u'Devon',
     u'user_full_name': u'Devon Bleibtrey',
     u'user_email': u'tpotandtom@gmail.com'}],
                          u'user_email': u'tyler_wiersing@gmail.com',
                          u'questions': [
                              {u'sb_score': 50, u'question_title': u'test',
                               u'question_content': u'example',
                               u'poster': u'tyler.wiersing@gmail.com'},
                              {u'sb_score': 50, u'question_title': u'test1',
                               u'question_content': u'example1',
                               u'poster': u'tyler.wiersing@gmail.com'},
                              {u'sb_score': 50, u'question_title': u'test2',
                               u'question_content': u'example2',
                               u'poster': u'tyler.wiersing@gmail.com'}]}, {
            u'user_relationships': [
                {u'user_last_name': u'Wiersing', u'user_first_name': u'Tyler',
                 u'user_full_name': u'Tyler Wiersing',
                 u'user_email': u'tyler.wiersing@gmail.com'},
                {u'user_last_name': u'Wiersing', u'user_first_name': u'Tyler',
                 u'user_full_name': u'Tyler Wiersing',
                 u'user_email': u'tyler.wiersing1@gmail.com'},
                {u'user_last_name': u'Bleibtrey', u'user_first_name': u'Devon',
                 u'user_full_name': u'Devon Bleibtrey',
                 u'user_email': u'tpotandtom@gmail.com'}],
            u'user_email': u'tpotandtom@gmail.com', u'questions': [
    {u'sb_score': 50, u'question_title': u'test',
     u'question_content': u'example', u'poster': u'tyler.wiersing@gmail.com'},
    {u'sb_score': 50, u'question_title': u'test1',
     u'question_content': u'example1', u'poster': u'tyler.wiersing@gmail.com'},
    {u'sb_score': 50, u'question_title': u'test2',
     u'question_content': u'example2',
     u'poster': u'tyler.wiersing@gmail.com'}]}]}
}

































test_search_index = {'sub_index_num': 1,
                      'sub_index_users': [
                          {'user_email': 'tyler_wiersing@gmail.com',
                           'questions': [{'question_title': 'test',
                                          'question_content': 'example',
                                          'sb_score': 50,
                                          'poster': 'tyler.wiersing@gmail.com'},
                                        {'question_title': 'test1',
                                          'question_content': 'example1',
                                          'sb_score': 50,
                                          'poster': 'tyler.wiersing@gmail.com'},
                                         {'question_title': 'test2',
                                          'question_content': 'example2',
                                          'sb_score': 50,
                                          'poster': 'tyler.wiersing@gmail.com'}],
                           'user_relationships': [{'user_email': 'tyler.wiersing@gmail.com',
                                      'user_first_name': 'Tyler',
                                      'user_last_name': 'Wiersing',
                                      'user_full_name': 'Tyler Wiersing'},
                                      {'user_email': 'tyler.wiersing1@gmail.com',
                                      'user_first_name': 'Tyler',
                                      'user_last_name': 'Wiersing',
                                      'user_full_name': 'Tyler Wiersing'},
                                      {'user_email': 'tpotandtom@gmail.com',
                                      'user_first_name': 'Devon',
                                      'user_last_name': 'Bleibtrey',
                                      'user_full_name': 'Devon Bleibtrey'}
                           ]
                          },
                          {'user_email': 'tpotandtom@gmail.com',
                           'questions': [{'question_title': 'test',
                                          'question_content': 'example',
                                          'sb_score': 50,
                                          'poster': 'tyler.wiersing@gmail.com'},
                                         {'question_title': 'test1',
                                          'question_content': 'example1',
                                          'sb_score': 50,
                                          'poster': 'tyler.wiersing@gmail.com'},
                                         {'question_title': 'test2',
                                          'question_content': 'example2',
                                          'sb_score': 50,
                                          'poster': 'tyler.wiersing@gmail.com'}],
                           'user_relationships': [{'user_email': 'tyler.wiersing@gmail.com',
                                      'user_first_name': 'Tyler',
                                      'user_last_name': 'Wiersing',
                                      'user_full_name': 'Tyler Wiersing'},
                                      {'user_email': 'tyler.wiersing1@gmail.com',
                                      'user_first_name': 'Tyler',
                                      'user_last_name': 'Wiersing',
                                      'user_full_name': 'Tyler Wiersing'},
                                      {'user_email': 'tpotandtom@gmail.com',
                                      'user_first_name': 'Devon',
                                      'user_last_name': 'Bleibtrey',
                                      'user_full_name': 'Devon Bleibtrey'}
                             ]
                         }]}

test_question_search_index = {
     'question_uuid': 'uuid',
     'question_title' : 'test',
     'question_content': 'test',
     'sb_score': 50,
     'poster': 'tyler.wiersing@gmail.com',
     'related_users': 'tpotandtom@gmail.com'}









