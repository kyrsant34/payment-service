# -*- coding: utf-8 -*-
from payment_service.app.backends.base import BasePaymentSystemClient

from .consts import (API_KEY, API_SECRET, DEPOSIT_URL, BANK_CODES, WITHDRAWAL_URL)
from .serializers import (DepositSerializer, WithdrawalSerializer, DepositNotificationSerializer,
                          WithdrawalNotificationSerializer)


class VisaClient(BasePaymentSystemClient):
    P_SUCCESS_CODE = '1'
    P_PROCESSING_CODE = '21'
    W_SUCCESS_CODE = '1'
    W_PROCESSING_CODE = '21'
    TIMEOUT = 15

    def make_deposit(self, data: dict) -> dict:
        serializer = DepositSerializer(data=dict(
            amount=int(data['amount']),
            currency=data['currency'],
            bank=self.get_bank_code(data.get('extra', {}).get('bank_code'),
                                    operation_type='deposit', **BANK_CODES),
            order_id=str(data['id']),
            client_id=data.get('extra', {}).get('client_id'),
            client_ip=data.get('extra', {}).get('client_ip')
        ), context={
            'key': API_KEY,
            'secret': API_SECRET,
            'uri': DEPOSIT_URL
        })
        validated_data = serializer.validate()
        signed_data = serializer.sign_data(validated_data)

        return dict(
            redirect_link=DEPOSIT_URL,
            redirect_method='POST',
            response_type='redirect',
            payload_data=signed_data,
            html=None
        )

    def make_withdrawal(self, data: dict) -> dict:
        serializer = WithdrawalSerializer(data=dict(
            amount=int(data['amount']),
            bank=self.get_bank_code(data.get('extra', {}).get('bank_code'),
                                    operation_type='withdrawal', **BANK_CODES),
            card_number=data.get('extra', {}).get('card_number'),
            name=data.get('extra', {}).get('cardholder_name'),
            state=data.get('extra', {}).get('province'),
            city=data.get('extra', {}).get('city'),
            order_id=str(data['id']),
        ), context={
            'key': API_KEY,
            'secret': API_SECRET,
            'uri': DEPOSIT_URL
        })

        validated_data = serializer.validate()
        signed_data = serializer.sign_data(validated_data)

        resp_data = self.retrying_call(WITHDRAWAL_URL, method='post', data=signed_data).json()

        ftp_response = resp_data.get('ftp_response')
        if ftp_response:
            code = ftp_response['code']
            message = ftp_response['message']
        else:
            message = resp_data.get('errors', '')
            code = None
        return {'code': code,
                'message': message}

    def parse_deposit_notification(self, data: dict) -> dict:
        serializer = DepositNotificationSerializer(data=data)
        validated_data = serializer.validate()
        return dict(
            code=validated_data['ftp_response[code]'],
            message=validated_data['ftp_response[message]'],
            transaction_id=validated_data['order_id']
        )

    def parse_withdrawal_notification(self, data) -> dict:
        serializer = WithdrawalNotificationSerializer(data=data)
        validated_data = serializer.validate()
        return dict(
            code=validated_data['ftp_response[code]'],
            message=validated_data['ftp_response[message]'],
            transaction_id=validated_data['order_id']
        )
