from unittest.mock import patch
import pytest

from payment_service.app.backends.visa.exceptions import (VisaDepositNotificationValidationError,
                                                              VisaWithdrawalNotificationValidationError)
from payment_service.app.backends.visa.serializers import (DepositNotificationSerializer,
                                                               WithdrawalNotificationSerializer)


class TestVisa:
    API_SECRET = 'n0BPhLQFedzYvXsgkcES7E9ToGfnomJm'

    @classmethod
    def setup_class(cls):
        patch('payment_service.app.backends.visa.serializers.API_SECRET', cls.API_SECRET).start()

    @classmethod
    def teardown_class(cls):
        patch.stopall()

    def test_signed_deposit_data_success(self):
        data = {'amount': '200000', 'auth_key': 'V4k3rgF3YUmkWbCfXDvQU1F3oVLyoGMU',
                'auth_signature': 'f6a8c77ca0289bfce015c74e07aed25d69462ad4ed576e395f5c2da70ee09f88',
                'auth_timestamp': '1532583482', 'auth_version': '1.0', 'code': '', 'ftp_response[code]': '2',
                'ftp_response[message]': 'Transaction failed', 'order_id': '3e1451e5-0589-4d42-a',
                'status': 'NOTOK', 'trans_id': 'xrjw]!jga9DPQXBj!e9Pj%WUn,c54x1]'}
        s = DepositNotificationSerializer(data=data)
        assert s.validate(), s.data

    def test_signed_deposit_data_fail(self):
        data = {'amount': '200000', 'auth_key': 'V4k3rgF3YUmkWbCfXDvQU1F3oVLyoGMU',
                'auth_signature': 'f6a8c77ca0289bfce015c74e07aed25d69462ad4ed577e395f5c2da70ee09f88',
                'auth_timestamp': '1532583482', 'auth_version': '1.0', 'code': '', 'ftp_response[code]': '2',
                'ftp_response[message]': 'Transaction failed', 'order_id': '3e1451e5-0589-4d42-a',
                'status': 'NOTOK', 'trans_id': 'xrjw]!jga9DPQXBj!e9Pj%WUn,c54x1]'}
        s = DepositNotificationSerializer(data=data)
        with pytest.raises(VisaDepositNotificationValidationError):
            s.validate()

    def test_signed_withdrawal_data_success(self):
        data = {'amount': '350000', 'auth_key': 'V4k3rgF3YUmkWbCfXDvQU1F3oVLyoGMU',
                'auth_signature': '2df6e50bff7bc92ca84945d856de59083ab2983f2658409f00100b18cae4e228',
                'auth_timestamp': '1532588947', 'auth_version': '1.0', 'code': '0000',
                'ftp_response[code]': '1', 'ftp_response[message]': 'Transaction successful',
                'order_id': 'b0889b09-3bcd-4261-b881-926c7b59c4b6', 'status': 'OK',
                'trans_id': '4*xBcC$(L9HKVKW2F1{oXquK(g~rPy]k'}
        s = WithdrawalNotificationSerializer(data=data)
        assert s.validate(), s.data

    def test_signed_withdrawal_data_fail(self):
        data = {'amount': '350000', 'auth_key': 'V4k3rgF3YUmkWbCfXDvQU1F3oVLyoGMU',
                'auth_signature': '2df6e50bff7bc92ca84945d856de59083ab2983f2658409f00100b23cae4e228',
                'auth_timestamp': '1532588947', 'auth_version': '1.0', 'code': '0000',
                'ftp_response[code]': '1', 'ftp_response[message]': 'Transaction successful',
                'order_id': 'b0889b09-3bcd-4261-b881-926c7b59c4b6', 'status': 'OK',
                'trans_id': '4*xBcC$(L9HKVKW2F1{oXquK(g~rPy]k'}
        s = WithdrawalNotificationSerializer(data=data)
        with pytest.raises(VisaWithdrawalNotificationValidationError):
            s.validate()
