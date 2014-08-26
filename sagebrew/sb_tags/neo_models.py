from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

class SBTag(StructuredNode):
    tag_name = StringProperty()
    tag_used = IntegerProperty()
    
    #relationships
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'POSTS_TAGGED')
    questions = RelationshipTo('sb_questions.neo_models.SBQuestion', 'QUESTION_TAGGED')

class SBAutoTag(SBTag):
    generated_from = StringProperty(default='alchemyapi')

    #
    answers = RelationshipTo('sb_answers.neo_models.SBAnswer', 'ANSWER_TAGGED')
