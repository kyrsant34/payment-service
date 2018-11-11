import json

import sqlalchemy.types as types


class JsonField(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, engine):
        if isinstance(value, dict):
            value = json.dumps(value)
        elif not isinstance(value, str):
            raise TypeError(f'invalid type JsonField - {value} (must be "str")')
        return value

    def process_result_value(self, value, engine):
        if value:
            return json.loads(value)
        return {}
