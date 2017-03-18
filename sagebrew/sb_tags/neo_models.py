from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo, StructuredRel, BooleanProperty,
                      FloatProperty)

from sagebrew.api.neo_models import SBObject


class TagRelevanceModel(StructuredRel):
    relevance = FloatProperty(default=0)


class FrequentTagModel(StructuredRel):
    count = IntegerProperty(default=1)
    in_sphere = BooleanProperty(default=False)


class Tag(SBObject):
    name = StringProperty(unique_index=True)
    tag_used = IntegerProperty(default=0)
    base = BooleanProperty(default=False)

    # relationships
    frequently_tagged_with = RelationshipTo('sagebrew.sb_tags.neo_models.Tag',
                                            'FREQUENTLY_TAGGED_WITH',
                                            model=FrequentTagModel)


class AutoTag(Tag):
    generated_from = StringProperty(default='alchemyapi')
