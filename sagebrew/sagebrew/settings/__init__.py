import socket

hostname = socket.gethostname()
if hostname == 'sagebrew':
    from production import *
elif hostname == 'staging-sagebrew':
    from staging import *
if('box' in hostname):
    from test import *
else:
    from development import *
