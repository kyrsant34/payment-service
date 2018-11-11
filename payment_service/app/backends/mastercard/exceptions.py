from payment_service.app.backends.exceptions import PaymentSystemException


class MasterCardException(PaymentSystemException):
    pass


class MasterCardDepositValidationError(MasterCardException):
    pass


class MasterCardDepositNotificationValidationError(MasterCardException):
    pass
