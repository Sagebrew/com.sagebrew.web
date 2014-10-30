import os


branch = os.environ.get("CIRCLE_BRANCH", None)
circle_ci = os.environ.get("CIRCLECI", False)
if circle_ci == "false":
    circle_ci = False
if circle_ci == "true":
    circle_ci = True
print circle_ci

if(circle_ci is True):
    print "here"
    from test import *
elif branch is None:
    print "branch None"
    from production import *
elif "dev" in branch:
    print "dev"
    from development import *
elif branch == "staging":
    print "branch staging"
    from staging import *
elif branch == "master":
    print "branch master"
    from production import *
else:
    print "else"
    from production import *
