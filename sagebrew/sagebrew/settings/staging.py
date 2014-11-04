from production import *

ALLOWED_HOSTS = ['staging.sagebrew.com', 'staging-web.sagebrew.com',
                 'sb-staging-web.elasticbeanstalk.com']

WEB_ADDRESS = "https://staging.sagebrew.com"
EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS
BROKER_TRANSPORT_OPTIONS["polling_interval"] = 3