import logging

from connexion import NoContent

from payment_service.app.backends.mastercard.client import MasterCardClient
from payment_service.app.backends.mastercard.serializers import MasterCardDepositNotificationValidationError
from payment_service.app.models import Transaction

logger = logging.getLogger(__name__)


def deposit_notification(request_data):
    client = MasterCardClient()
    logger.info(f'mastercard deposit notification {request_data}')
    try:
        validated_data = client.parse_deposit_notification(request_data)
    except Exception as err:
        logger.error(f'{MasterCardDepositNotificationValidationError.__class__}, {err}')
        return NoContent, 400

    # FIXME combine with VISA
    transaction = Transaction.query.filter_by(id=validated_data['transaction_id']).first()
    status = client.get_status_by_code(validated_data['code'])
    transaction.update(status=status)

    transaction.send_callback()
    return NoContent, 200
