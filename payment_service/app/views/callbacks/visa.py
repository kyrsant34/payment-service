import logging

from connexion import NoContent

from payment_service.app.backends.visa.client import VisaClient
from payment_service.app.backends.visa.serializers import (VisaDepositNotificationValidationError,
                                                               VisaWithdrawalNotificationValidationError)
from payment_service.app.models import Transaction

logger = logging.getLogger(__name__)


def deposit_notification(request_data):
    client = VisaClient()
    logger.info(f'visa deposit notification {request_data}')
    try:
        validated_data = client.parse_deposit_notification(request_data)
    except Exception as err:
        logger.error(f'{VisaDepositNotificationValidationError.__class__}, {err}')
        return NoContent, 400

    transaction = Transaction.query.filter_by(id=validated_data['transaction_id']).first()
    status = client.get_status_by_code(validated_data['code'])
    transaction.update(status=status)

    transaction.send_callback()
    return NoContent, 200


def withdrawal_notification(request_data):
    client = VisaClient()
    logger.info(f'visa withdrawal notification {request_data}')
    try:
        validated_data = client.parse_withdrawal_notification(request_data)
    except Exception as err:
        logger.error(f'{VisaWithdrawalNotificationValidationError.__class__}, {err}')
        return NoContent, 400

    transaction = Transaction.query.filter_by(id=validated_data['transaction_id']).first()
    status = client.get_status_by_code(validated_data['code'])
    transaction.update(status=status)

    transaction.send_callback()
    return NoContent, 200
