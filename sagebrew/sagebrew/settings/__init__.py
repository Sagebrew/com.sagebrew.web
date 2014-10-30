import os


branch = os.environ.get("CIRCLE_BRANCH", None)
circle_ci = os.environ.get("CIRCLECI", False)
if circle_ci == "false":
    circle_ci = False
if circle_ci == "true":
    circle_ci = True

if(circle_ci):
    from test import *
elif branch is None:
    from production import *
elif "dev" in branch:
    from development import *
elif branch == "staging":
    from staging import *
elif branch == "master":
    from production import *
else:
    from production import *
