import pytest

from payment_service.app.models import Transaction


@pytest.mark.parametrize("country", ('CHN', 'JPN'))
def test_create_transaction(client, app, delete_after_post, country):
    response = client.request(app.op['payment_service.app.views.transaction.create'](
        transaction_data=dict(
            service_id='stat-service',
            account_id=1231,
            type='DEPOSIT',
            amount=100.00,
            currency='CNY',
            country=country,
            callback='http://test/callback',
            extra=dict(
                client_id='412',
                client_ip='172.16.0.1',
                bank_code='ABC',
                client_email='lala@gmail.com',
            )
        )
    ))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 201, content
    assert response.data['id']
    assert response.data['payment_system_data']['response_type'] == 'redirect', content
    delete_after_post(Transaction, response.data['id'])


def test_transaction_by_id(client, app, generate_transaction, delete_after_post):
    transaction = generate_transaction(dict(backend='VISA'))
    response = client.request(app.op['payment_service.app.views.transaction.get_by_id'](transaction_id=transaction.id))
    content = str(response.raw).replace('\\n', '')
    assert response.status == 200, content
    assert response.data['id'] == transaction.id
    assert response.data['status'] == Transaction.STATUS_NEW
    delete_after_post(Transaction, transaction.id)


def test_transaction_list(client, app, generate_transaction, delete_after_post):
    transaction = generate_transaction(dict(backend='VISA'))
    response = client.request(app.op['payment_service.app.views.transaction.list']())
    content = str(response.raw).replace('\\n', '')
    assert response.status == 200, content
    assert len(response.data) > 1
    delete_after_post(Transaction, transaction.id)
