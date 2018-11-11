from payment_service.app.backends.mastercard.consts import DEPOSIT_URL, SECRET_KEY
from payment_service.app.backends.mastercard.serializers import DepositNotificationSerializer
from payment_service.app.models import Transaction


def test_deposit_redirection(client, app, delete_after_post):
    response = client.request(app.op['payment_service.app.views.transaction.create'](
        transaction_data=dict(
            service_id='stat-service',
            account_id=1231,
            type='DEPOSIT',
            amount="112.00",
            currency='CNY',
            country='JPN',  # country='JPN' corresponds to backend='MASTERCARD'
            callback='http://test/callback',
            extra=dict(
                client_email='lala@gmail.com',
            )
        )
    ))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 201, content
    assert response.data['id']
    assert response.data['payment_system_data']['response_type'] == 'redirect', content
    assert response.data['payment_system_data']['redirect_link'] == DEPOSIT_URL, content
    assert response.data['status'] == Transaction.STATUS_PENDING
    check_status_on_backend(response.data['id'], Transaction.STATUS_PENDING, client, app)
    delete_after_post(Transaction, response.data['id'])


def test_deposit_callback(client, app, generate_transaction, delete_after_post):
    transaction = generate_transaction(dict(backend='MASTERCARD',
                                            type='DEPOSIT',
                                            status=Transaction.STATUS_PENDING))
    request_data = {
        'status': 'APPROVED',
        'number': f'{transaction.id}',
        'amount': f'{transaction.amount}',
        'currency': f'{transaction.currency}',
    }

    s = DepositNotificationSerializer(request_data, context=dict(key=SECRET_KEY))
    request_data = s.sign_data(request_data)

    response = client.request(app.op['payment_service.app.views.callbacks.mastercard.deposit_notification'](
        request_data=request_data
    ))
    assert response.status == 200, str(response.raw).replace('\\n', '')
    check_status_on_backend(transaction.id, Transaction.STATUS_SUCCEDED, client, app)
    delete_after_post(Transaction, transaction.id)


def test_deposit_failed_callback(client, app, generate_transaction, delete_after_post):
    transaction = generate_transaction(dict(backend='MASTERCARD',
                                            type='DEPOSIT',
                                            status=Transaction.STATUS_PENDING))
    request_data = {
        'status': 'DENIED',
        'number': f'{transaction.id}',
        'amount': f'{transaction.amount}',
        'currency': f'{transaction.currency}',
    }

    s = DepositNotificationSerializer(request_data, context=dict(key=SECRET_KEY))
    request_data = s.sign_data(request_data)

    response = client.request(app.op['payment_service.app.views.callbacks.mastercard.deposit_notification'](
        request_data=request_data
    ))
    assert response.status == 200, str(response.raw).replace('\\n', '')
    check_status_on_backend(transaction.id, Transaction.STATUS_FAILED, client, app)
    delete_after_post(Transaction, transaction.id)


def test_callback_with_wrong_sign(client, app, generate_transaction, delete_after_post):
    transaction = generate_transaction(dict(backend='MASTERCARD',
                                            type='DEPOSIT',
                                            status=Transaction.STATUS_PENDING))
    request_data = {
        'status': 'APPROVED',
        'number': f'{transaction.id}',
        'amount': f'{transaction.amount}',
        'currency': f'{transaction.currency}',
    }

    s = DepositNotificationSerializer(request_data, context=dict(key=SECRET_KEY))
    request_data = s.sign_data(request_data)
    request_data['sha512'] += '0'

    response = client.request(app.op['payment_service.app.views.callbacks.mastercard.deposit_notification'](
        request_data=request_data
    ))
    assert response.status == 400, str(response.raw).replace('\\n', '')
    check_status_on_backend(transaction.id, Transaction.STATUS_PENDING, client, app)
    delete_after_post(Transaction, transaction.id)


def test_callback_with_wrong_parameters(client, app, generate_transaction, delete_after_post):
    transaction = generate_transaction(dict(backend='MASTERCARD',
                                            type='DEPOSIT',
                                            status=Transaction.STATUS_PENDING))
    # without "status"
    request_data = {
        # 'status': 'APPROVED',
        'number': f'{transaction.id}',
        'amount': f'{transaction.amount}',
        'currency': f'{transaction.currency}',
    }

    s = DepositNotificationSerializer(request_data, context=dict(key=SECRET_KEY))
    request_data = s.sign_data(request_data)

    response = client.request(app.op['payment_service.app.views.callbacks.mastercard.deposit_notification'](
        request_data=request_data
    ))
    assert response.status == 400, str(response.raw).replace('\\n', '')
    check_status_on_backend(transaction.id, Transaction.STATUS_PENDING, client, app)
    delete_after_post(Transaction, transaction.id)


def check_status_on_backend(t_id, status, client, app):
    client.init_request()
    response = client.request(app.op['payment_service.app.views.transaction.get_by_id'](transaction_id=t_id))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 200, content
    assert response.data['id'] == t_id
    assert response.data['status'] == status
