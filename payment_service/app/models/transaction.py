import datetime
import logging
import requests

from payment_service.app.json_field import JsonField
from payment_service.extensions import db

from .base import ModelMixin


logger = logging.getLogger(__name__)


class StatusMixin(ModelMixin):
    STATUS_NEW = 'NEW'
    STATUS_PENDING = 'PENDING'
    STATUS_FAILED = 'FAILED'
    STATUS_SUCCEDED = 'SUCCEDED'

    STATUSES = (STATUS_NEW, STATUS_PENDING, STATUS_FAILED, STATUS_SUCCEDED)

    status = db.Column(db.String(30), nullable=False, default=STATUS_NEW)

    @classmethod
    def validate_status(cls, data):
        data['status'] = data.get('status', cls.STATUS_NEW)
        return data


class BackendMixin(ModelMixin):
    BACKENDS = {
        'MASTERCARD': 'payment_service.app.backends.MasterCardClient',
        'VISA': 'payment_service.app.backends.VisaClient',
        'MIR': 'payment_system.backends.MIRClient',
    }

    backend = db.Column(db.String(30), nullable=False)

    @classmethod
    def validate_backend(cls, data):
        val = data.get('backend')
        if val not in cls.BACKENDS:
            raise f"'backend': {val} - is not valid"
        return data


class Transaction(StatusMixin, BackendMixin, db.Model):
    TRANSACTION_TYPE_DEPOSIT = 'DEPOSIT'
    TRANSACTION_TYPE_WITHDRAWAL = 'WITHDRAWAL'

    TRANSACTION_TYPES = (TRANSACTION_TYPE_DEPOSIT, TRANSACTION_TYPE_WITHDRAWAL)

    id = db.Column(db.Integer(), primary_key=True)
    service_id = db.Column(db.String(30))
    account_id = db.Column(db.Integer(), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.DECIMAL(precision=20, scale=2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    country = db.Column(db.String(30), nullable=False)
    callback = db.Column(db.String(255), nullable=False)
    extra = db.Column(JsonField(2048))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def create(cls, **data):
        data = cls.validate_status(data)
        data = cls.validate_backend(data)
        return super().create(**data)

    def send_callback(self):
        try:
            requests.post(self.callback, data=self.serialize())
            return True
        except (requests.exceptions.RequestException, TimeoutError) as exc:
            logger.error(f"can't send notification data (transaction id={self.id}) to {self.callback} - {exc}")
            return False
