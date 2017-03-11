import os

branch = os.environ.get("BRANCH", None)

if branch is None:
    from development import *
else:
    from production import *
