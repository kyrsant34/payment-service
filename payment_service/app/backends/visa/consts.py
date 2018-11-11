# -*- coding: utf-8 -*-
import os

DEPOSIT_URL = os.getenv('VISA_DEPOSIT_URL', 'https://visa.com/api/deposit/')
WITHDRAWAL_URL = os.getenv('VISA_WITHDRAWAL_URL', 'https://visa.com/api/withdrawal/')
MERCHANT_NO = os.getenv('VISA_MERCHANT_NO', '33')
VERSION = os.getenv('VISA_VERSION', '1.0')

API_SECRET = os.getenv('VISA_API_SECRET', 'HTQaupSfsdfsfsIOgffsdfs')
API_KEY = os.getenv('VISA_API_KEY', 'HTQaupGSDsdGSfsIOgffsdfs')

BANK_CODES = {
    'deposit': {
        'ABC': '01030000',
        'BOB': '04031000',
        'CCB': '01050000',
        'CEBB': '03030000',
        'CMBC': '03050000',
        'ICBC': '01020000',
        'PSBC': '01000000',
        'SHB': '04012900',
    },
    'withdrawal': {
        'ICBC': '102100099996',
        'ABC': '103100000026',
        'BOC': '104100000004',
    }
}
