from payment_service.app.models import Transaction
from payment_service.app.utils import import_string
import logging

logger = logging.getLogger("gunicorn.info")


def get_backend_by_country(country):
    map_dict = {
        'JPN': 'MASTERCARD',
        'CHN': 'VISA',
    }
    backend = map_dict.get(country)
    if backend is None:
        raise RuntimeError({'error': f'unknown "country": {country}'})
    return backend


def create(transaction_data):
    transaction_data['backend'] = get_backend_by_country(transaction_data['country'])
    try:
        transaction = Transaction.create(**transaction_data)
    except Exception as exc:
        logger.error(str(exc))
        return str(exc), 400

    response = transaction.serialize()
    ps_client = import_string(Transaction.BACKENDS[transaction.backend])()
    if transaction.type == Transaction.TRANSACTION_TYPE_DEPOSIT:
        result = ps_client.make_deposit(response)
        response['status'] = Transaction.STATUS_PENDING
    elif transaction.type == Transaction.TRANSACTION_TYPE_WITHDRAWAL:
        result = ps_client.make_withdrawal(response)
        response['status'] = ps_client.get_status_by_code(result['code'])
    else:
        raise RuntimeError(f'unknown transaction type - {transaction.type}')
    logger.info(f'{ps_client.__class__} result: {result}')
    transaction.update(status=response['status'])
    response['payment_system_data'] = result
    return response, 201


def get_by_id(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    if transaction:
        return transaction.serialize(), 200
    else:
        return f"Transaction ('id': {transaction_id}) - not found", 404


def list():
    transactions = Transaction.query.all()
    return [transaction.serialize() for transaction in transactions], 200
