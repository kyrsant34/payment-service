import os

from payment_service.config.default import *  # NOQA


SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(
    os.environ.get('MYSQL_USER', 'root'),
    os.environ.get('MYSQL_PASSWORD'),
    os.environ.get('MYSQL_HOST', 'mysql'),
    os.environ.get('MYSQL_DATABASE')
)

DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
