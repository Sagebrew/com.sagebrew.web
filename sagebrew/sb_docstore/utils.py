from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import JSONResponseError

from sb_base.decorators import apply_defense
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion
from sb_comments.neo_models import SBComment

conn = DynamoDBConnection(
    host='192.168.1.136',
    port=8000,
    aws_secret_access_key='anything',
    is_secure=False
)

@apply_defense
def add_object_to_table(table_name, object_data):
    '''
    This function will attempt to add an object to a table, this will be
    used to build each table and build the docstore. This is a generalized
    function and will work for every table
    :param table_name:
    :param object_data:
    :return:
    '''
    try:
        table = Table(table_name=table_name, connection=conn)
    except JSONResponseError:
        return False #TODO review this return
    table.put_item(data=object_data)
    return True

@apply_defense
def get_object(table_name, hash_key, range_key=None):
    try:
        table = Table(table_name=table_name)
    except JSONResponseError:
        return False #TODO review this return
    table.get_item()

@apply_defense
def build_question_page(question_uuid, question_table, solution_table):
    '''
    This function will build a question page, it will take the question table
    and solution table which will be:
    'private_questions'
    'private_solutions'
    'public_questions'
    'public_solutions'
    Then it will build the page into the docstore.
    This includes getting the question object, all the comments associated
    with it and all the solutions associated with it.

    :param question_uuid:
    :param question_table:
    :param solution_table:
    :return:
    '''
    #TODO should we store rendered html of the page in the docstore?
    #this would cut down on cpu time of rendering pages since we would only
    #have to render the page once and only render when it gets updated
    #TODO implement comments for questions and solutions
    question = SBQuestion.nodes.get(sb_id=question_uuid)
    question_dict = question.get_single_question_dict()
    answer_dicts = question_dict.pop('answers', None)
    question_dict['object_uuid'] = question_dict.pop('question_uuid', None)
    add_object_to_table(table_name=question_table, object_data=question_dict)
    for answer in answer_dicts:
        answer['parent_object'] = question_dict['object_uuid']
        answer['object_uuid'] = answer.pop('answer_uuid', None)
        add_object_to_table(table_name=solution_table, object_data=answer)






