from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty)

class TagRelevanceModel(StructuredRel):
    relevance = FloatProperty(default=0)

class FrequentTagModel(StructuredRel):
    count = IntegerProperty(default=1)

class SBTag(StructuredNode):
    tag_name = StringProperty(unique_index=True)
    tag_used = IntegerProperty(default=0)
    
    #relationships
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'POSTS_TAGGED')
    questions = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'QUESTION_TAGGED')

class SBAutoTag(SBTag):
    generated_from = StringProperty(default='alchemyapi')

    #
    answers = RelationshipTo('sb_answers.neo_models.SBAnswer', 'ANSWER_TAGGED')
    frequently_auto_tagged_with = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                                                 'FREQUENTLY_AUTO_TAGGED_WITH',
                                                 model=FrequentTagModel)
