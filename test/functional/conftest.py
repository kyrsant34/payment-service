import functools
import os

import pytest
from pyswagger import App
from pyswagger.contrib.client.requests import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from payment_service.config import settings
from payment_service.extensions import db
from payment_service.app.models import Transaction


@pytest.fixture(autouse=True)
def sqlalchemy_():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
    db.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return db


@pytest.fixture(autouse=True)
def client():
    c = Client()

    def init_request(self):
        self.request = functools.partial(self.request, opt={
            'url_netloc': 'backend:8000'
        })
    c.init_request = functools.partial(init_request, c)

    c.init_request()

    return c


@pytest.fixture(autouse=True)
def app():
    spec_path = os.path.join(os.path.dirname(__file__), '..', '..', 'share', 'api', 'swagger.yml')
    return App.create(spec_path)


@pytest.fixture(autouse=True)
def delete_after_post(sqlalchemy_):
    def clean(model, id):
        item = model.query.get(id)
        sqlalchemy_.session.delete(item)
        sqlalchemy_.session.commit()
        assert model.query.filter_by(id=id).first() is None
    return clean


@pytest.fixture()
def generate_transaction(sqlalchemy_):
    transaction_data = dict(
        service_id='stat-service',
        account_id=1231,
        type='DEPOSIT',
        amount=100.00,
        currency='CNY',
        country='CHN',
        callback='http://test/callback',
        extra=dict(
            client_id='412',
            client_ip='172.16.0.1',
            bank_code='ABC',
        )
    )

    def create(data=None):
        if data:
            transaction_data.update(data)
        item = Transaction(**transaction_data)
        sqlalchemy_.session.add(item)
        sqlalchemy_.session.commit()
        assert Transaction.query.filter_by(id=item.id).first()
        return item

    return create
