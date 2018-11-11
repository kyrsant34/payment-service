# -*- coding: utf-8 -*-
# import base64
# import hashlib
# import hmac
from collections import OrderedDict
# from urllib.parse import quote

# from Crypto.Hash import MD5, SHA1


def sloppy_encode(data) -> str:
    _sorted = sorted(data.items(), key=lambda t: t[0])
    result = '&'.join([f'{key}={value}' for key, value in _sorted])
    return result


def get_ordered_dict(d: dict) -> OrderedDict:
    return OrderedDict(sorted(d.items(), key=lambda x: x[0]))


# def get_hmac_signature(key: str,
#                        message: str,
#                        digestmod=hashlib.sha1) -> str:
#     key = bytes(key, 'utf-8')
#     message = bytes(message, 'utf-8')
#     sign = hmac.new(key, message, digestmod=digestmod).digest()
#     dig64 = base64.b64encode(sign).decode()
#     sign = quote(dig64)
#     return sign
#
#
# def get_sha1_signature(text: str) -> str:
#     text = bytearray(text, encoding='UTF-8')
#     h = SHA1.new()
#     h.update(text)
#     return h.hexdigest()
#
#
# def get_md5_signature(text: str) -> str:
#     text = bytearray(text, encoding='UTF-8')
#     h = MD5.new()
#     h.update(text)
#     return h.hexdigest()
