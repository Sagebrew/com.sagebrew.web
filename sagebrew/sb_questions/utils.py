from dateutil import parser

from neomodel import db

from sb_comments.serializers import CommentSerializer
from sb_comments.neo_models import Comment
from .serializers import QuestionSerializerNeo


def question_html_snapshot(request, question, question_uuid, tags,
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
    single_object['tags'] = tags
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
