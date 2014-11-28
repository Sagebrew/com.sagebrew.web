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

def create_table():
    users = Table('users', connection=conn)
    users.delete()

    users = Table.create('users', schema=[
        HashKey('email', data_type=STRING),
        RangeKey('last_name', data_type=STRING),
    ],  throughput={
        'read': 5,
        'write': 15,
    },
    connection=conn)
    '''
    friends = Table.create('friends', schema=[
        HashKey('account_type', data_type=NUMBER),
        RangeKey('last_name'),
    ], throughput={
        'read': 5,
        'write': 15
    }, indexes=[
        AllIndex('EverythingIndex', parts=[
            HashKey('account_type', data_type=NUMBER),
            RangeKey('last_name')
        ])
    ], connection=conn)
    '''
    print users.describe()
    users.put_item(data={
        'email': 'tyler.wiersing@gmail.com',
        'last_name': 'Wiersing',
        'other': 'this is some other information'
    }, overwrite=True)

    me = users.query_2(email__eq='tyler.wiersing@gmail.com')
    for item in me:
        print item['email']
