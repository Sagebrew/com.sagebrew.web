from json import loads
from django.core.management.base import BaseCommand
from django.conf import settings

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, AllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import STRING, NUMBER

conn = DynamoDBConnection(
    host='192.168.1.136',
    port=8000,
    aws_secret_access_key='anything',
    is_secure=False
)


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates the required DynamoDB tables.'

    def create_dynamo_tables(self):
        with open('%s/temp_files/dynamo_table.js'%settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            for item in data:
                if 'range_key' and 'local_index' in item.keys():
                    Table.create(item['table_name'], schema=[
                        HashKey(item['hash_key'], data_type=STRING),
                        RangeKey(item['range_key']),
                    ], indexes=[
                        AllIndex('district_index', parts=[
                            HashKey(item['hash_key']),
                            RangeKey(item['local_index'], STRING),
                            RangeKey(item['range_key']),
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