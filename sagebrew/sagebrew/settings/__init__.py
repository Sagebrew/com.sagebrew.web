import socket

hostname = socket.gethostname()
if 'kepric' in hostname:
    from development import *
elif hostname == 'staging-sagebrew':
    from staging import *
elif('box' in hostname):
    from test import *
else:
    from production import *
