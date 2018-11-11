import base64
import decimal

import xmltodict

from payment_service.app.backends.base import BasePaymentSystemSerializer
from .exceptions import MasterCardDepositValidationError, MasterCardDepositNotificationValidationError
from .utils import get_sha512_signature


class Serializer(BasePaymentSystemSerializer):

    def verify_signed_data(self, signed_data: dict) -> bool:
        xml_data = base64.b64decode(signed_data['orderXML']).decode('UTF-8')
        sha512_data = get_sha512_signature(xml_data + self.context['key'])

        # convert keys {'@status': ...} -> {'status': ...}
        self.data = {param[1:]: val for param, val in xmltodict.parse(xml_data)['order'].items()}
        return sha512_data == signed_data['sha512']

    def sign_data(self, data: dict) -> dict:
        sloppy_data = "<order"
        for field_name in data:
            sloppy_data += f' {field_name}="{data[field_name]}"'
        sloppy_data += '/>'
        order_as_sha512 = get_sha512_signature(sloppy_data + self.context['key'])
        base64_data = base64.b64encode(bytes(sloppy_data, 'UTF-8')).decode("utf-8")

        return dict(
            orderXML=base64_data,
            sha512=order_as_sha512
        )


class DepositSerializer(Serializer):
    FIELDS = (
        ('wallet_id', None, int),
        ('number', None, str),
        ('description', '', str),
        ('currency', 'CNY', str),
        ('amount', None, decimal.Decimal),
        ('email', None, str),
        ('locale', 'en', str),
    )
    EXCEPTION_CLASS = MasterCardDepositValidationError


class DepositNotificationSerializer(Serializer):
    FIELDS = (
        ('status', None, str),
        ('number', None, str),
        ('amount', None, str),
        ('currency', None, str),
    )

    EXCEPTION_CLASS = MasterCardDepositNotificationValidationError

    def validate(self) -> dict:
        if not self.verify_signed_data(self.data):
            raise self.EXCEPTION_CLASS(f'"sign" is not valid - {self.data}')
        validated_data = super().validate()
        return validated_data
