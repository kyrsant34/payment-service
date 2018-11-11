# -*- coding: utf-8 -*-


class PaymentSystemException(Exception):

    @classmethod
    def validate_type(cls, data, key, _type):
        val = data.get(key)
        if not isinstance(val, _type):
            raise cls(f'{key}: {val} must be {_type} type')
