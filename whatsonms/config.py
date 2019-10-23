import os


# The domainName and stage that comprise the websocket endpoint
WS_DOMAIN = os.environ.get('WS_DOMAIN')
WS_STAGE = os.environ.get('WS_STAGE')

# The URL_PREFIX is the path behind which the app will be served
# when using a reverse proxy (eg. API Gateway).
URL_PREFIX = os.environ.get('URL_PREFIX', '/whats-on')

# These settings are optional and will be strictly used for Sentry reporting.
RELEASE = os.environ.get('RELEASE', None)
ENV = os.environ.get('ENV', None)

TABLE_METADATA = os.environ.get('DEMO_TABLE_METADATA')
# TABLE_METADATA = os.environ.get(os.environ.get('ENV', None).upper() + '_' + 'TABLE_METADATA')
TABLE_SUBSCRIBERS = os.environ.get('DEMO_TABLE_SUBSCRIBERS')
