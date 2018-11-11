# -*- coding: utf-8 -*-
import logging

from payment_service.app.backends.base import BasePaymentSystemClient
from .consts import DEPOSIT_URL, MERCHANT_ID, SECRET_KEY
from .serializers import DepositSerializer, DepositNotificationSerializer

logger = logging.getLogger(__name__)


class MasterCardClient(BasePaymentSystemClient):
    P_SUCCESS_CODE = 'APPROVED'
    P_PROCESSING_CODE = 'PENDING'
    W_SUCCESS_CODE = 'APPROVED'
    W_PROCESSING_CODE = 'PENDING'

    def make_deposit(self, data: dict) -> dict:
        serializer = DepositSerializer(
            data=dict(
                wallet_id=MERCHANT_ID,
                number=f'{data["id"]}',
                description=f'Deposit {data["id"]}',
                currency=data['currency'],
                amount=data["amount"],
                email=data.get('extra', {}).get('client_email'),
                locale=data.get('extra', {}).get('locale', 'en'),
            ), context=dict(
                key=SECRET_KEY,
            ))

        validated_data = serializer.validate()
        signed_data = serializer.sign_data(validated_data)

        return dict(
            response_type='redirect',
            redirect_link=DEPOSIT_URL,
            redirect_method='POST',
            payload_data=signed_data,
            html=None
        )

    def parse_deposit_notification(self, data: dict) -> dict:
        serializer = DepositNotificationSerializer(data=data, context=dict(key=SECRET_KEY))
        validated_data = serializer.validate()

        return dict(
            code=validated_data['status'],
            transaction_id=validated_data['number'],
            amount=validated_data['amount'],
            currency=validated_data['currency'],
        )
