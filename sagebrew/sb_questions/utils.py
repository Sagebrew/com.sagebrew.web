from dateutil import parser

from django.template.loader import render_to_string
from django.core.cache import cache

from neomodel import DoesNotExist, CypherException, db

from sb_base.decorators import apply_defense
from plebs.neo_models import Pleb
from sb_comments.serializers import CommentSerializer
from sb_comments.neo_models import Comment
from .serializers import QuestionSerializerNeo
from .neo_models import Question


@apply_defense
def prepare_question_search_html(question_uuid):
    question = cache.get(question_uuid)
    if question is None:
        try:
            question = Question.nodes.get(object_uuid=question_uuid)
        except(Question.DoesNotExist, DoesNotExist):
            return False
        except(CypherException, IOError):
            return None
        cache.set(question_uuid, question)

    query = "MATCH (p:Pleb {username: '%s'}) RETURN p" % (
        question.owner_username)
    try:
        res, col = db.cypher_query(query=query)
        owner = Pleb.inflate(res[0][0])
    except (CypherException, IOError, IndexError):
        return None
    question_dict = QuestionSerializerNeo(question).data
    question_dict['first_name'] = owner.first_name
    question_dict['last_name'] = owner.last_name
    question_dict['created'] = parser.parse(question_dict['created'])
    question_dict['last_edited_on'] = parser.parser(
        question_dict['last_edited_on'])
    rendered = render_to_string('conversation_block.html', question_dict)

    return rendered


def question_html_snapshot(request, question, question_uuid, keywords,
                           description):
    single_object = QuestionSerializerNeo(
        question, context={'request': request,
                           'expand_param': True}).data
    query = 'MATCH (q:Question {object_uuid: "%s"})-' \
            '[:HAS_A]->(c:Comment) WHERE c.to_be_deleted=False ' \
            'RETURN c' % question_uuid
    res, _ = db.cypher_query(query)
    queryset = [Comment.inflate(row[0]) for row in res]
    single_object['last_edited_on'] = parser.parse(
        single_object['last_edited_on'])
    single_object['uuid'] = question.object_uuid
    single_object['sort_by'] = 'uuid'
    single_object['description'] = description
    single_object['keywords'] = keywords
    single_object['html_snapshot'] = True
    single_object['comments'] = CommentSerializer(
        queryset, many=True, context={'request': request,
                                      'expand_param': True}).data
    for comment in single_object['comments']:
        comment['last_edited_on'] = parser.parse(
            comment['last_edited_on'])
    for solution in single_object['solutions']:
        query = 'MATCH (s:Solution {object_uuid: "%s"})-' \
                '[:HAS_A]->(c:Comment) RETURN c' % solution['object_uuid']
        res, _ = db.cypher_query(query)
        queryset = [Comment.inflate(row[0]) for row in res]
        solution['comments'] = CommentSerializer(
            queryset, many=True, context={'request': request,
                                          'expand_param': True}).data
        for comment in solution['comments']:
            comment['last_edited_on'] = parser.parse(
                comment['last_edited_on'])
        solution['last_edited_on'] = parser.parse(
            solution['last_edited_on'])
    return single_object
