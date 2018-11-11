from payment_service.app.backends.exceptions import PaymentSystemException


class VisaException(PaymentSystemException):
    pass


class VisaDepositValidationError(VisaException):
    pass


class VisaWithdrawalValidationError(VisaException):
    pass


class VisaDepositNotificationValidationError(VisaException):
    pass


class VisaWithdrawalNotificationValidationError(VisaException):
    pass
