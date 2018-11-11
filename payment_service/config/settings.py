import os
import importlib


PROJECT_STACK = os.environ.get('PROJECT_STACK', 'dev')

PROJECT_STACK_SETTINGS = importlib.import_module(
    f'payment_service.config.{PROJECT_STACK}'
)

for k in dir(PROJECT_STACK_SETTINGS):
    globals()[k] = PROJECT_STACK_SETTINGS.__dict__[k]
