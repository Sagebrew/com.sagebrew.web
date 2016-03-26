from neomodel import (StringProperty, DateTimeProperty,
                      IntegerProperty, FloatProperty, ArrayProperty,
                      RelationshipTo)

from sb_base.neo_models import TitledContent


class NewsArticle(TitledContent):
    """
    Missions are what a Quest is currently focused on doing. They encompass
    what it is trying to achieve whether it be running for office or advocating
    for something. A mission allows a Quest to take donations and for other
    Quests to endorse another Quest's missions.
    """
    # The source from which we received the article. Valid Options are:
    #     sb_crawler
    #     webhose
    #     alchemyapi
    provider = StringProperty(default="webhose")
    external_id = StringProperty(unique_index=True)
    url = StringProperty()
    summary = StringProperty()
    site_full = StringProperty()
    site = StringProperty()
    site_section = StringProperty()
    section_title = StringProperty()
    title = StringProperty(index=True)
    title_full = StringProperty()
    highlight_title = StringProperty()
    highlight_text = StringProperty()
    # Language that the article is in. Valid Options:
    #     english
    language = StringProperty()
    published = DateTimeProperty()
    replies_count = IntegerProperty()
    participants_count = IntegerProperty()
    # What type of site is this? Valid Options:
    #     blogs
    #     news
    #     forum
    #     comments
    site_type = StringProperty()
    country = StringProperty()
    spam_score = FloatProperty()
    main_image = StringProperty()
    # Scale of 0-10, 0 being the worst and 10 being the best
    performance_score = IntegerProperty()
    crawled = DateTimeProperty()

    # Optimization
    external_links = ArrayProperty()
    persons = ArrayProperty()
    locations = ArrayProperty()
    organizations = ArrayProperty()
    author = StringProperty()

    images = RelationshipTo('sb_uploads.neo_models.UploadedObject',
                            'IMAGE_ON_PAGE')
