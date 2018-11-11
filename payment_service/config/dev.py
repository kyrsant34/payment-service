import os

from payment_service.config.default import *  # NOQA


DEBUG = True

SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(
    os.environ.get('MYSQL_USER', 'root'),
    os.environ.get('MYSQL_PASSWORD'),
    os.environ.get('MYSQL_HOST', 'db'),
    os.environ.get('MYSQL_DATABASE')
)

DOMAIN_NAME = 'http://backend:8000'

SENTRY_CONFIG = {}
