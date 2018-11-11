from sqlalchemy.inspection import inspect
from sqlalchemy.orm.collections import InstrumentedList

from payment_service.extensions import db


class Serializer:

    def serialize(self, stop_type=False):
        result = {}
        for c in inspect(self).attrs.keys():
            if not isinstance(getattr(self, c), InstrumentedList):
                if not isinstance(getattr(self, c), db.Model):
                    result[c] = getattr(self, c)
            else:
                result[c] = [m.serialize() for m in getattr(self, c)]
        return result


class ModelMixin:

    def serialize(self):
        return Serializer.serialize(self)

    @classmethod
    def create(cls, **data):
        obj = cls(**data)
        db.session.add(obj)
        db.session.commit()
        return obj

    def update(self, **data):
        for param in data:
            setattr(self, param, data[param])
        db.session.commit()

    def __repr__(self):
        res = f'{self.__class__.__name__}'
        if hasattr(self, 'id'):
            res = f'{res} {self.id}'
        return res
