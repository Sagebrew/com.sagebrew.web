from production import *

ALLOWED_HOSTS = ['staging.sagebrew.com', ]

S3_URL = "https://d3bfx8awejj0jg.cloudfront.net/"
WEB_ADDRESS = "https://staging.sagebrew.com"
EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS
BROKER_TRANSPORT_OPTIONS["polling_interval"] = 30
