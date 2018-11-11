import os


DEBUG = False

SENTRY_CONFIG = {
    'dsn': 'https://564a314875d84a96a8e5d49ad168116c:fd2e316c786b407992a1fc37e799b69c@sentry.io/1229700',
    'environment': os.environ.get('PROJECT_STACK', 'dev'),
    'release': os.environ.get('PROJECT_VERSION', None)
}

SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_TRACK_MODIFICATIONS = True

DOMAIN_NAME = '127.0.0.1:8000'
SQLALCHEMY_MODEL_IMPORTS = (
    'payment_service.app.models',
)
