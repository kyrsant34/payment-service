# -*- coding: utf-8 -*-
from Crypto.Hash import SHA512


def get_sha512_signature(text: str) -> str:
    text = bytearray(text, encoding='UTF-8')
    h = SHA512.new()
    h.update(text)
    return h.hexdigest()
