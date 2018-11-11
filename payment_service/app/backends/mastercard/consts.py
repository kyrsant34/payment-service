import os

DEPOSIT_URL = os.getenv('MASTERCARD_DEPOSIT_URL', 'https://sandbox.mastercard.com/api/deposit/')
MERCHANT_ID = os.getenv('MASTERCARD_MERCHANT_ID', 5555)
SECRET_KEY = os.getenv('MASTERCARD_SECRET_KEY', 'u0BUHAg3Gfq4')
