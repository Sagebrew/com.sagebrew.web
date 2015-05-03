from time import sleep
from subprocess import call

from django.test.runner import DiscoverRunner


class SBTestRunner(DiscoverRunner):
    def setup_databases(self, *args, **kwargs):
        call("sudo service neo4j-service stop", shell=True)
        sleep(1)
        success = call("/webapps/neo-test/neo4j-community-2.1.7/bin/neo4j"
                       " start-no-wait", shell=True)
        if success != 0:
            return False
        sleep(10)
        from neomodel import db
        query = "start n=node(*) optional match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        super(SBTestRunner, self).__init__(*args, **kwargs)

    def teardown_databases(self, old_config, **kwargs):
        from neomodel import db
        query = "start n=node(*) optional match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        sleep(1)
        success = call("/webapps/neo-test/neo4j-community-2.1.7/bin/neo4j"
                       " stop", shell=True)
        if success != 0:
            return False
        sleep(1)
        call("sudo service neo4j-service start", shell=True)
