from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      RelationshipTo, StructuredRel, BooleanProperty,
                      FloatProperty)


class TagRelevanceModel(StructuredRel):
    relevance = FloatProperty(default=0)


class FrequentTagModel(StructuredRel):
    count = IntegerProperty(default=1)
    in_sphere = BooleanProperty(default=False)


class SBTag(StructuredNode):
    tag_name = StringProperty(unique_index=True)
    tag_used = IntegerProperty(default=0)
    base = BooleanProperty(default=False)
    
    #relationships
    frequently_tagged_with = RelationshipTo('sb_tag.neo_models.SBTag',
                                            'FREQUENTLY_TAGGED_WITH',
                                            model=FrequentTagModel)


class SBAutoTag(SBTag):
    generated_from = StringProperty(default='alchemyapi')

