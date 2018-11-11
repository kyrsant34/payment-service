# -*- coding: utf-8 -*-
from copy import deepcopy
import hashlib
import hmac
import time
from urllib.parse import urljoin

from payment_service.app.backends.utils import sloppy_encode
from .consts import API_KEY, API_SECRET, VERSION
from .exceptions import (VisaDepositValidationError, VisaWithdrawalValidationError, VisaException,
                         VisaDepositNotificationValidationError, VisaWithdrawalNotificationValidationError)

from payment_service.config import settings
from payment_service.app.backends.base import BasePaymentSystemSerializer


class Serializer(BasePaymentSystemSerializer):
    EXCEPTION_CLASS = VisaException

    def get_signature(self, payload: str, method: str, uri: str, secret: str) -> str:
        payload = '\n'.join([method, uri, payload])
        return hmac.new(bytes(secret, 'utf-8'),
                        bytes(payload, 'utf-8'),
                        hashlib.sha256).hexdigest()

    def sign_data(self, data: dict, prefix: str = 'auth_') -> dict:
        signed_data = deepcopy(data)
        signed_data.update({
            prefix + 'version': self.context.get('version', VERSION),
            prefix + 'key': self.context['key'],
            prefix + 'timestamp': int(time.time()),
        })
        payload = sloppy_encode(signed_data)
        signature = self.get_signature(payload,
                                       'POST',
                                       'ftp',
                                       self.context['secret'])
        signed_data[prefix + 'signature'] = signature
        return signed_data

    def verify_signed_data(self, signed_data: dict) -> bool:
        sloppy_data = deepcopy(signed_data)
        auth_signature = sloppy_data.pop('auth_signature')
        sloppy_data = sloppy_encode(sloppy_data)
        expected_auth_signature = self.get_signature(sloppy_data, 'POST', 'ftp', API_SECRET)
        return expected_auth_signature == auth_signature


class DepositSerializer(Serializer):
    FIELDS = (
        ('action', 'initTransaction', str),
        ('api_key', API_KEY, str),
        ('amount', None, int),
        ('currency', 'CNY', str),
        ('order_id', None, str),
        ('client_id', None, str),
        ('client_ip', None, str),
        ('bank', None, str),
        ('card', '01', str),
    )
    EXCEPTION_CLASS = VisaDepositValidationError

    def validate(self) -> dict:
        validated_data = super().validate()
        validated_data['callback_url'] = urljoin(settings.DOMAIN_NAME, 'api/v1.0/callbacks/visa/deposit')
        validated_data['return_url'] = urljoin(settings.DOMAIN_NAME, 'deposit')
        validated_data['amount'] *= 100
        return validated_data


class WithdrawalSerializer(Serializer):
    FIELDS = (
        ('card_number', None, str),
        ('api_key', API_KEY, str),
        ('amount', None, int),
        ('order_id', None, str),
        ('name', None, str),
        ('state', None, int),
        ('city', None, int),
        ('bank', None, str),
    )
    EXCEPTION_CLASS = VisaWithdrawalValidationError

    def validate(self) -> dict:
        validated_data = super().validate()
        validated_data['callback_url'] = urljoin(settings.DOMAIN_NAME, 'api/v1.0/callbacks/visa/withdrawal')
        validated_data['return_url'] = urljoin(settings.DOMAIN_NAME, 'withdrawal')
        validated_data['amount'] *= 100
        return validated_data


class NotificationSerializer(Serializer):

    def validate(self) -> dict:
        if not self.verify_signed_data(self.data):
            raise self.EXCEPTION_CLASS(f'"sign" is not valid - {self.data}')
        validated_data = super().validate()
        return validated_data


class DepositNotificationSerializer(NotificationSerializer):
    FIELDS = (
        ('trans_id', '', str),
        ('status', '', str),
        ('order_id', None, str),
        ('ftp_response[message]', '', str),
        ('ftp_response[code]', None, str),
    )
    EXCEPTION_CLASS = VisaDepositNotificationValidationError


class WithdrawalNotificationSerializer(NotificationSerializer):
    FIELDS = (
        ('status', '', str),
        ('order_id', None, str),
        ('ftp_response[message]', '', str),
        ('ftp_response[code]', None, str),
    )
    EXCEPTION_CLASS = VisaWithdrawalNotificationValidationError
