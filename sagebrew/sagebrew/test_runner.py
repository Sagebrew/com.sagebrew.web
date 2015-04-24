from os import environ
from subprocess import call

from django.test.runner import DiscoverRunner


class SBTestRunner(DiscoverRunner):
    def setup_databases(self, *args, **kwargs):
        call("/webapps/neo-test/neo4j-community-2.1.7/bin/neo4j start",
             shell=True)
        environ['NEO4J_REST_URL'] = "http://127.0.0.1:8484/db/data/"
        super(SBTestRunner, self).__init__(*args, **kwargs)

    def teardown_databases(self, old_config, **kwargs):
        from neomodel import db
        query = "start n=node(*) optional match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        call("/webapps/neo-test/neo4j-community-2.1.7/bin/neo4j stop",
             shell=True)
        environ['NEO4J_REST_URL'] = "http://127.0.0.1:7474/db/data/"
