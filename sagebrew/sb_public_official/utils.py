from django.core.cache import cache

from neomodel import db, DoesNotExist

from .neo_models import PublicOfficial


def determine_reps(pleb):
    # Remove all existing relationships with pleb
    query = 'MATCH (pleb:Pleb {username: "%s"}) ' \
            'WITH pleb ' \
            'OPTIONAL MATCH (pleb)-[senators:HAS_SENATOR]->' \
            '(:PublicOfficial) WITH pleb, senators ' \
            'OPTIONAL MATCH (pleb)-[house_reps:HAS_HOUSE_REPRESENTATIVE]' \
            '-(:PublicOfficial) DELETE senators, house_reps' % pleb.username
    res, _ = db.cypher_query(query)

    # Link pleb with their house representative
    query = 'MATCH (pleb:Pleb {username: "%s"})-[:LIVES_AT]->' \
            '(address:Address) ' \
            'WITH pleb, address ' \
            'MATCH (public:PublicOfficial) ' \
            'WHERE public.state=address.state ' \
            'AND public.district=toInt(address.congressional_district) ' \
            'CREATE UNIQUE (pleb)-[:HAS_HOUSE_REPRESENTATIVE]->(public) ' \
            'RETURN public' % pleb.username
    res, _ = db.cypher_query(query)
    if res.one:
        cache.set("%s_house_representative" % pleb.username,
                  PublicOfficial.inflate(res.one))

    # Link pleb with their senator
    query = 'MATCH (pleb:Pleb {username: "%s"})-[:LIVES_AT]->' \
            '(address:Address) ' \
            'WITH pleb, address ' \
            'MATCH (public:PublicOfficial) ' \
            'WHERE public.state=address.state ' \
            'AND public.district=0 ' \
            'CREATE UNIQUE (pleb)-[:HAS_SENATOR]->(public) ' \
            'RETURN DISTINCT public' % pleb.username
    res, _ = db.cypher_query(query)
    senators = [PublicOfficial.inflate(row[0]) for row in res]
    if senators:
        cache.set("%s_senators" % pleb.username, senators)
    try:
        president = PublicOfficial.nodes.get(title='President')
        pleb.president.connect(president)
    except(DoesNotExist, PublicOfficial.DoesNotExist):
        pass
    cache.delete(pleb.username)
    cache.delete('%s_possible_house_representatives' %
                 pleb.username)
    cache.delete('%s_possible_senators' % pleb.username)
    return True
