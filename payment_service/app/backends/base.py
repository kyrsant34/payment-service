# -*- coding: utf-8 -*-
from abc import abstractmethod
import logging
import requests
import time

from payment_service.app.models.transaction import StatusMixin
from .exceptions import PaymentSystemException


logger = logging.getLogger(__name__)


class BasePaymentSystemSerializer:
    FIELDS = ()
    EXCEPTION_CLASS = PaymentSystemException

    def __init__(self, data: dict, context: dict = None) -> None:
        self.data = data
        self.context = context

    def validate(self) -> dict:
        validated_data = dict()
        for key, default, _type in self.FIELDS:
            validated_data[key] = self.data.get(key, default)
            self.EXCEPTION_CLASS.validate_type(validated_data, key, _type)
        return validated_data


class BasePaymentSystemClient:
    TIMEOUT = 3

    def __init__(self, cert_path: str = None):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        session = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=5)
        session.mount('https://', a)

        if cert_path:
            session.cert = cert_path
            session.verify = False
        self.session = session

    def get_bank_code(self, val: str, operation_type=None, **codes):
        code = None
        if not codes.get('all') and not codes.get('withdrawal') and not codes.get('deposit'):
            return val
        elif operation_type == 'deposit' and codes.get('deposit'):
            code = codes['deposit'].get(val)
        elif operation_type == 'withdrawal' and codes.get('withdrawal'):
            code = codes['withdrawal'].get(val)
        elif codes.get('all'):
            code = codes['all'].get(val)

        if not code:
            raise Exception(
                {'bank': 'Problems with the bank, use another one'})

        return code

    @abstractmethod
    def get_bank_name(self, raw_bank_code: str):
        raise NotImplementedError

    @abstractmethod
    def make_deposit(self, data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def make_withdrawal(self, data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def parse_deposit_notification(self, data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def parse_withdrawal_notification(self, data: dict) -> dict:
        raise NotImplementedError

    def get_status_by_code(self, code):
        if code in (self.P_SUCCESS_CODE, self.W_SUCCESS_CODE):
            status = StatusMixin.STATUS_SUCCEDED
        elif code in (self.P_PROCESSING_CODE, self.W_PROCESSING_CODE):
            status = StatusMixin.STATUS_PENDING
        else:
            status = StatusMixin.STATUS_FAILED
        return status

    def retrying_call(self, url, method=None, data=None):
        attempts = 3
        repeat_time = 3
        while True:
            try:
                response = getattr(self, method)(url, data)
                logger.info(f'{response.status_code} {response.content}')
                return response
            except TimeoutError:
                attempts -= 1
                if attempts == 0:
                    raise
                time.sleep(repeat_time)
                repeat_time *= 2

    def post(self, url, data=None):
        response = self.session.post(url, data=data, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response
