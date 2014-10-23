from production import *

ALLOWED_HOSTS = ['*']

WEB_ADDRESS = "https://staging.sagebrew.com"
EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS