from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

class FrequentTagModel(StructuredRel):
    count = IntegerProperty(default=0)

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
    frequently_auto_tagged_with = RelationshipTo('sb_tags.neo_models.SBAutoTag',
                                                 'FREQUENTLY_AUTO_TAGGED_WITH',
                                                 model=FrequentTagModel)
