import pytest
# import requests

from payment_service.app.backends.visa.consts import API_KEY, API_SECRET, DEPOSIT_URL
from payment_service.app.backends.visa.serializers import Serializer
from payment_service.app.models import Transaction


# def test_deposit_workflow(client, app, delete_after_post):
#     response = client.request(app.op['payment_service.app.views.transaction.create'](
#         transaction_data=dict(
#             service_id='stat-service',
#             account_id=1231,
#             type='DEPOSIT',
#             amount="112.00",
#             currency='CNY',
#             country='CHN',  # country='CHN' corresponds to backend='VISA'
#             callback='http://test/callback',
#             extra=dict(
#                 client_id='412',
#                 client_ip='172.16.0.1',
#                 bank_code='ABC',
#             )
#         )
#     ))
#     content = str(response.raw).replace('\\n', '')
#     assert response.status == 201, content
#     assert response.data['id']
#     assert response.data['payment_system_data']['response_type'] == 'redirect', content
#     assert response.data['payment_system_data']['redirect_link'] == DEPOSIT_URL, content
#     delete_after_post(Transaction, response.data['id'])
#
#     res = requests.post(DEPOSIT_URL, response.data['payment_system_data']['payload_data'])
#     with open('visa_deposit.html', 'w') as f:
#         f.write(res.content.decode('utf-8'))


def test_deposit_redirection(client, app, delete_after_post):
    response = client.request(app.op['payment_service.app.views.transaction.create'](
        transaction_data=dict(
            service_id='stat-service',
            account_id=1231,
            type='DEPOSIT',
            amount="112.00",
            currency='CNY',
            country='CHN',  # country='CHN' corresponds to backend='VISA'
            callback='http://test/callback',
            extra=dict(
                client_id='412',
                client_ip='172.16.0.1',
                bank_code='ABC',
            )
        )
    ))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 201, content
    assert response.data['id']
    assert response.data['payment_system_data']['response_type'] == 'redirect', content
    assert response.data['payment_system_data']['redirect_link'] == DEPOSIT_URL, content
    delete_after_post(Transaction, response.data['id'])


@pytest.mark.parametrize("t_type", ('DEPOSIT', 'WITHDRAWAL'))
def test_callbacks(client, app, generate_transaction, delete_after_post, t_type):
    transaction = generate_transaction(dict(backend='VISA', type=t_type, status=Transaction.STATUS_PENDING))
    request_data = {
        'ftp_response[code]': '1',
        'ftp_response[message]': 'transaction successful',
        'order_id': f'{transaction.id}',
        'status': 'success',
    }
    s = Serializer(request_data, context=dict(key=API_KEY, secret=API_SECRET))
    request_data = s.sign_data(request_data)
    response = client.request(app.op[f'payment_service.app.views.callbacks.visa.{t_type.lower()}_notification'](
        request_data=request_data
    ))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 200, content
    check_status_on_backend(transaction.id, Transaction.STATUS_SUCCEDED, client, app)
    delete_after_post(Transaction, transaction.id)


@pytest.mark.parametrize("t_type", ('DEPOSIT', 'WITHDRAWAL'))
def test_failed_callbacks(client, app, generate_transaction, delete_after_post, t_type):
    transaction = generate_transaction(dict(backend='VISA', type=t_type, status=Transaction.STATUS_PENDING))
    request_data = {
        'ftp_response[code]': '3',
        'ftp_response[message]': 'transaction failed',
        'order_id': f'{transaction.id}',
        'status': 'failed',
    }
    s = Serializer(request_data, context=dict(key=API_KEY, secret=API_SECRET))
    request_data = s.sign_data(request_data)
    response = client.request(app.op[f'payment_service.app.views.callbacks.visa.{t_type.lower()}_notification'](
        request_data=request_data
    ))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 200, content
    check_status_on_backend(transaction.id, Transaction.STATUS_FAILED, client, app)
    delete_after_post(Transaction, transaction.id)


@pytest.mark.parametrize("t_type", ('DEPOSIT', 'WITHDRAWAL'))
def test_callbacks_with_wrong_sign(client, app, generate_transaction, delete_after_post, t_type):
    transaction = generate_transaction(dict(backend='VISA', type=t_type, status=Transaction.STATUS_PENDING))
    request_data = {
        'ftp_response[code]': '1',
        'ftp_response[message]': 'transaction successful',
        'order_id': f'{transaction.id}',
        'status': 'success',
    }
    s = Serializer(request_data, context=dict(key=API_KEY, secret=API_SECRET))
    request_data = s.sign_data(request_data)
    request_data['auth_signature'] += '0'
    response = client.request(app.op[f'payment_service.app.views.callbacks.visa.{t_type.lower()}_notification'](
        request_data=request_data
    ))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 400, content
    check_status_on_backend(transaction.id, Transaction.STATUS_PENDING, client, app)
    delete_after_post(Transaction, transaction.id)


@pytest.mark.parametrize("t_type", ('DEPOSIT', 'WITHDRAWAL'))
def test_callbacks_with_wrong_parameters(client, app, generate_transaction, delete_after_post, t_type):
    transaction = generate_transaction(dict(backend='VISA', type=t_type, status=Transaction.STATUS_PENDING))
    request_data = {
        'ftp_response[code]': '1',
        'ftp_response[message]': 'transaction successful',
        'status': 'success',
    }
    s = Serializer(request_data, context=dict(key=API_KEY, secret=API_SECRET))
    request_data = s.sign_data(request_data)
    with pytest.raises(ValueError):
        client.request(app.op[f'payment_service.app.views.callbacks.visa.{t_type.lower()}_notification'](
            request_data=request_data
        ))
    check_status_on_backend(transaction.id, Transaction.STATUS_PENDING, client, app)
    delete_after_post(Transaction, transaction.id)


def check_status_on_backend(t_id, status, client, app):
    client.init_request()
    response = client.request(app.op['payment_service.app.views.transaction.get_by_id'](transaction_id=t_id))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 200, content
    assert response.data['id'] == t_id
    assert response.data['status'] == status
