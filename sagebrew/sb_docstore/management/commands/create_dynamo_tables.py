from json import loads
from django.core.management.base import BaseCommand
from django.conf import settings

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.fields import (HashKey, RangeKey, KeysOnlyIndex,
                                   AllIndex, GlobalAllIndex)
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import STRING, NUMBER
from boto.dynamodb2.exceptions import JSONResponseError

from sb_docstore.utils import connect_to_dynamo




class Command(BaseCommand):
    args = 'None.'
    help = 'Creates the required DynamoDB tables.'

    def create_dynamo_tables(self):
        with open('%s/sb_docstore/management/commands'
                  '/dynamo_table.js'%settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            conn = connect_to_dynamo()
            for item in data:
                try:
                    table = Table(table_name=item['table_name'],
                                  connection=conn)
                    table.describe()
                    table.delete()
                except JSONResponseError:
                    print 'The table %s does not exist'%item['table_name']
                try:
                    if 'range_key' and 'local_index' in item.keys():
                        Table.create(item['table_name'], schema=[
                            HashKey(item['hash_key'], data_type=STRING),
                            RangeKey(item['range_key']),
                        ], indexes=[
                            AllIndex(item['local_index_name'], parts=[
                                HashKey(item['hash_key']),
                                RangeKey(item['local_index'],
                                         data_type=item['type']),
                            ])
                        ],throughput={
                            'read': 15,
                            'write': 15
                        }, connection=conn)
                    elif 'range_key' in item.keys():
                        Table.create(item['table_name'], schema=[
                            HashKey(item['hash_key'], data_type=STRING),
                            RangeKey(item['range_key']),
                        ], throughput={
                            'read': 15,
                            'write': 15
                        }, connection=conn)
                    else:
                        Table.create(item['table_name'], schema=[
                            HashKey(item['hash_key'], data_type=STRING),
                        ], throughput={
                            'read': 15,
                            'write': 15
                        }, connection=conn)
                except JSONResponseError:
                    print 'Table %s already exists' % item['table_name']
        '''
        users = Table.create('users-full', schema=[
            HashKey('email', data_type=STRING),
            RangeKey('last_name', data_type=STRING),
        ],  throughput={
            'read': 5,
            'write': 15,
        },
        connection=conn)
        '''

    def handle(self, *args, **options):
        self.create_dynamo_tables()
        self.stdout.write('Created Dynamo Tables')