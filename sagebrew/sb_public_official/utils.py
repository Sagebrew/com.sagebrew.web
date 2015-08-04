import logging
from django.core.cache import cache

from neomodel import (DoesNotExist, CypherException)

from plebs.neo_models import Pleb
from api.utils import execute_cypher_query
from sb_base.decorators import apply_defense

from .neo_models import (PublicOfficial)

logger = logging.getLogger('loggly_logs')


@apply_defense
def determine_reps(username):
    senators = []
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError):
        return False
    try:
        address = pleb.address.all()[0]
    except (CypherException, IOError, IndexError):
        logger.exception("Determine Reps Cypher Exception")
        return False
    pleb_state = address.state
    pleb_district = int(address.congressional_district)
    try:
        query = 'match (n:PublicOfficial) where n.state="%s" ' \
            ' return n' % pleb_state
        reps, meta = execute_cypher_query(query)
    except (CypherException, IOError, IndexError):
        logger.exception("Determine Reps Cypher Exception")
        return False
    for rep in pleb.house_rep.all():
        pleb.house_rep.disconnect(rep)
    for senator in pleb.senators.all():
        pleb.senators.disconnect(senator)
    reps = [PublicOfficial.inflate(row[0]) for row in reps]
    cache.delete("%s_house_representative" % username)
    cache.delete("%s_senators" % username)
    for rep in reps:
        if rep.district == pleb_district:
            try:
                pleb.house_rep.connect(rep)
                cache.set("%s_house_representative" % username, rep)
            except (CypherException, IOError):
                logger.exception("Determine Reps Cypher Exception")
                return False
        if rep.district == 0:
            try:
                pleb.senators.connect(rep)
            except (CypherException, IOError):
                logger.exception("Determine Reps Cypher Exception")
                return False
            senators.append(rep)
    president = PublicOfficial.nodes.get(title='President')
    pleb.president.connect(president)
    cache.set("%s_senators" % username, senators)
    # Need this as neomodel does not currently support spawning post_save
    # after connections
    pleb.refresh()
    cache.set(pleb.username, pleb)
    return True
