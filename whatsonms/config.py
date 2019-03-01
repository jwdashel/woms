import os


DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE')

# The URL_PREFIX is the path behind which the app will be served
# when using a reverse proxy (eg. API Gateway).
URL_PREFIX = os.environ.get('URL_PREFIX', '/whats-on')

# These settings are optional and will be strictly used for Sentry reporting.
RELEASE = os.environ.get('RELEASE', None)
ENV = os.environ.get('ENV', None)
