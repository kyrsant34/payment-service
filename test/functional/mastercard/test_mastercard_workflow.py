from datetime import datetime
import time
import os
from selenium.webdriver.support.ui import Select
import pytest

from payment_service.app.models import Transaction
from selenium import webdriver

from payment_service.app.backends.mastercard.serializers import DepositNotificationSerializer
from payment_service.app.backends.mastercard.consts import SECRET_KEY
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from test.functional import conftest


@pytest.mark.release
class TestMasterCardDeposit:
    DEPOSIT_URL = 'https://sandbox.mastercard.com/MI/mastercardment.html'
    SCREENSHOT_FOLDER = 'share/test/payment_systems/mastercard/'

    def setup(self):
        self.pyswagger_client = conftest.client()
        self.app = conftest.app()
        self.browser = webdriver.Remote(command_executor='http://selenium-hub:4444/wd/hub',
                                        desired_capabilities=DesiredCapabilities.CHROME)
        self.init_script = open('test/functional/mastercard/init_deposit_form.js').read()
        self.dt_format = '%Y%m%d_%H%M%S'
        os.makedirs(self.SCREENSHOT_FOLDER, exist_ok=True)

    def teardown(self):
        self.browser.quit()

    @property
    def client(self):
        self.pyswagger_client.init_request()
        return self.pyswagger_client

    def test_deposit_workflow(self, delete_after_post):
        data = self.create_deposit_on_backend()
        self.check_status_on_backend(data['id'], Transaction.STATUS_PENDING)

        self.init_form_step_1(data['payment_system_data'])
        self.fill_form_step_2()
        self.submit_form_step_3()
        payment_status_title = self.browser.find_element_by_id('payment-status-title')
        assert 'Decline' == payment_status_title.text

        self.send_success_notification(data['id'], data['amount'], data['currency'])
        self.check_status_on_backend(data['id'], Transaction.STATUS_SUCCEDED)

        delete_after_post(Transaction, data['id'])

    def send_success_notification(self, transaction_id, amount, currency):
        request_data = {
            'status': 'APPROVED',
            'number': f'{transaction_id}',
            'amount': f'{amount}',
            'currency': f'{currency}',
        }

        s = DepositNotificationSerializer(request_data, context=dict(key=SECRET_KEY))
        request_data = s.sign_data(request_data)

        response = self.client.request(self.app.op['payment_service.app.views.callbacks.mastercard.deposit_notification'](
            request_data=request_data
        ))
        assert response.status == 200, str(response.raw).replace('\\n', '')

    def check_status_on_backend(self, transaction_id, status):
        response = self.client.request(
            self.app.op['payment_service.app.views.transaction.get_by_id'](transaction_id=transaction_id))
        content = str(response.raw).replace('\\n', '')
        assert response.status == 200, content
        assert response.data['id'] == transaction_id
        assert response.data['status'] == status

    def create_deposit_on_backend(self):
        response = self.client.request(self.app.op['payment_service.app.views.transaction.create'](
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
        assert response.data['payment_system_data']['payload_data']['orderXML'], response.data
        assert response.data['payment_system_data']['payload_data']['sha512'], response.data
        return response.data

    def init_form_step_1(self, data):
        assert data['redirect_method'] == 'POST', data
        params = data['payload_data']

        self.browser.execute_script(f'url="{self.DEPOSIT_URL}"; params={params}; {self.init_script}')
        self.save_screenshot('step_1')

        assert 'Card Details' in self.browser.page_source

    def fill_form_step_2(self):
        card_number = self.browser.find_element_by_id('input-card-number')
        card_number.send_keys('622908328049426212')
        card_holder_name = self.browser.find_element_by_id('input-card-holder')
        card_holder_name.send_keys('MARK Zuckerberg')
        card_expires_month = Select(self.browser.find_element_by_id('card-expires-month'))
        card_expires_month.select_by_index(2)
        card_expires_year = Select(self.browser.find_element_by_id('card-expires-year'))
        card_expires_year.select_by_index(2)
        input_card_cvc = self.browser.find_element_by_id('input-card-cvc')
        input_card_cvc.send_keys('313')
        self.save_screenshot('step_2')

    def submit_form_step_3(self):
        btn_submit = self.browser.find_element_by_id('action-submit')
        btn_submit.click()
        time.sleep(3)
        self.save_screenshot('step_3')

    def save_screenshot(self, name):
        dt = datetime.now().strftime(self.dt_format)
        path = f'{self.SCREENSHOT_FOLDER}{dt}_{name}.png'
        self.browser.save_screenshot(path)
