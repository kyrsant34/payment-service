import importlib
import logging

import connexion

from raven.contrib.flask import Sentry

from payment_service.config import settings
from payment_service.extensions import db

__all__ = [
    'app'
]

logging.basicConfig(level=logging.INFO)

app = connexion.App(__name__, specification_dir='../share/api/', strict_validation=True)
# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml', arguments={'title': 'Payment Service API'})
wsgi_app = app.app  # expose global WSGI application object
wsgi_app.config.from_object(settings)


with wsgi_app.app_context():
    for module in wsgi_app.config.get('SQLALCHEMY_MODEL_IMPORTS', list()):
        importlib.import_module(module)
db.init_app(wsgi_app)

sentry = Sentry(wsgi_app)


if __name__ == '__main__':
    wsgi_app.run(host='0.0.0.0', port=8000, debug=True)
