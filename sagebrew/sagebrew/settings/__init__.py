import socket
from os import environ

hostname = socket.gethostname()
branch = environ.get("CIRCLE_BRANCH", None)
if branch is None:
    from production import *
elif "dev" in branch:
    from development import *
elif branch == "staging":
    from staging import *
elif branch == "master":
    from production import *
else:
    from production import *
