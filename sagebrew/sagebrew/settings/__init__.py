import socket

if socket.gethostname() == 'sagebrew':
    PROJECT_DIR = Path(__file__).ancestor(4)
    repo_name = PROJECT_DIR[PROJECT_DIR.rfind('/') + 1:]
    if ('-production' in repo_name):
        from production import *
    if ('-qa' in repo_name):
        from qa import *
    if ('-staging' in repo_name):
        from staging import *
    if ('-uat' in repo_name):
        from uat import *

else:

    from development import *
